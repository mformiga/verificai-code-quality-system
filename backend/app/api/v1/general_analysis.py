"""
General analysis endpoints for VerificAI Backend - STO-007
"""

from typing import List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.analysis import Analysis, AnalysisStatus
from app.models.prompt import Prompt, PromptCategory
from app.models.prompt import GeneralCriteria, GeneralAnalysisResult as GeneralAnalysisResultModel
from app.schemas.analysis import AnalysisCreate, AnalysisResponse
from app.api.v1.analysis import process_analysis
from app.services.prompt_service import get_prompt_service
from app.services.llm_service import llm_service

router = APIRouter()


class GeneralAnalysisRequest(BaseModel):
    """Request model for general analysis"""
    name: str
    description: Optional[str] = None
    file_paths: List[str]
    criteria: List[str]
    llm_provider: str = "openai"
    temperature: float = 0.7
    max_tokens: int = 4000


class AnalyzeSelectedRequest(BaseModel):
    """Request model for analyzing selected criteria"""
    criteria_ids: List[str]
    file_paths: List[str]
    analysis_name: Optional[str] = "Análise de Critérios Gerais"
    temperature: float = 0.7
    max_tokens: int = 4000
    is_reanalysis: Optional[bool] = False
    result_id_to_update: Optional[int] = None


class GeneralCriteriaResponse(BaseModel):
    """Criteria model for general analysis"""
    id: str
    text: str
    active: bool = True


class CriterionCreate(BaseModel):
    """Request model for creating a criterion"""
    text: str


class GeneralAnalysisResult(BaseModel):
    """Result model for general analysis"""
    id: str
    analysis_type: str = "general"
    timestamp: Any
    overall_assessment: str
    criteria_results: List[dict]
    token_usage: dict
    processing_time: float
    status: str


class AnalysisResultUpdate(BaseModel):
    """Request model for updating analysis result"""
    criteria_key: str
    criteria_data: dict


@router.post("/create", response_model=AnalysisResponse)
async def create_general_analysis(
    request: GeneralAnalysisRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Create a general analysis with custom criteria"""
    # Create or get general prompt
    general_prompt = db.query(Prompt).filter(
        Prompt.name == "General Analysis",
        Prompt.category == PromptCategory.GENERAL,
        Prompt.author_id == current_user.id
    ).first()

    if not general_prompt:
        # Create general prompt with user criteria
        criteria_text = "\n".join([f"- {criterion}" for criterion in request.criteria])
        prompt_content = f"""
You are a code quality expert. Analyze the provided code based on the following criteria:

{criteria_text}

For each criterion, provide:
1. A clear assessment of whether the code meets the criterion
2. Confidence level (0.0-1.0)
3. Specific evidence from the code
4. Recommendations for improvement if applicable

Provide your analysis in a structured format that includes:
- Overall assessment
- Individual criterion evaluations
- Code examples supporting your findings
- Actionable recommendations

Format your response in markdown.
"""
        general_prompt = Prompt(
            name="General Analysis",
            content=prompt_content,
            category=PromptCategory.GENERAL,
            author_id=current_user.id,
            is_public=False
        )
        db.add(general_prompt)
        db.commit()
        db.refresh(general_prompt)
    else:
        # Update prompt content with new criteria
        criteria_text = "\n".join([f"- {criterion}" for criterion in request.criteria])
        prompt_content = f"""
You are a code quality expert. Analyze the provided code based on the following criteria:

{criteria_text}

For each criterion, provide:
1. A clear assessment of whether the code meets the criterion
2. Confidence level (0.0-1.0)
3. Specific evidence from the code
4. Recommendations for improvement if applicable

Provide your analysis in a structured format that includes:
- Overall assessment
- Individual criterion evaluations
- Code examples supporting your findings
- Actionable recommendations

Format your response in markdown.
"""
        general_prompt.content = prompt_content
        db.commit()

    # Create analysis
    analysis_data = AnalysisCreate(
        name=request.name,
        description=request.description,
        prompt_id=general_prompt.id,
        file_paths=request.file_paths,
        configuration={
            "llm_provider": request.llm_provider,
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
            "criteria": request.criteria,
            "analysis_type": "general"
        }
    )

    analysis = Analysis(
        **analysis_data.dict(),
        user_id=current_user.id,
        status=AnalysisStatus.PENDING
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    # Start background processing
    background_tasks.add_task(process_analysis, analysis.id, db)

    return analysis


@router.get("/criteria")
async def get_user_criteria(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get shared criteria from all users"""
    try:
        # Get all criteria from database (shared access)
        all_criteria = db.query(GeneralCriteria).filter(
            GeneralCriteria.is_active == True
        ).order_by(GeneralCriteria.order, GeneralCriteria.created_at).all()

        # Deduplicate by text and convert to response format
        seen_texts = set()
        result = []
        for criterion in all_criteria:
            if criterion.text not in seen_texts:
                seen_texts.add(criterion.text)
                result.append({
                    "id": f"criteria_{criterion.id}",
                    "text": criterion.text,
                    "active": criterion.is_active
                })

        return result
    except Exception as e:
        print(f"ERROR in get_user_criteria: {e}")
        import traceback
        traceback.print_exc()
        raise e


@router.post("/criteria", response_model=GeneralCriteriaResponse)
async def create_criteria(
    request: CriterionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Create a new criterion"""
    # Get the highest order number for this user
    max_order = db.query(GeneralCriteria).filter(
        GeneralCriteria.user_id == current_user.id
    ).order_by(GeneralCriteria.order.desc()).first()

    next_order = (max_order.order + 1) if max_order else 0

    # Create new criterion
    new_criterion = GeneralCriteria(
        user_id=current_user.id,
        text=request.text,
        is_active=True,
        order=next_order
    )

    db.add(new_criterion)
    db.commit()
    db.refresh(new_criterion)

    # Return created criterion
    return GeneralCriteriaResponse(
        id=f"criteria_{new_criterion.id}",
        text=new_criterion.text,
        active=new_criterion.is_active
    )


@router.put("/criteria/{criteria_id}", response_model=GeneralCriteriaResponse)
async def update_criteria(
    criteria_id: str,
    request: CriterionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Update an existing criterion"""
    # Extract the actual ID from the criteria_id string
    try:
        actual_id = int(criteria_id.replace("criteria_", ""))
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid criteria ID format"
        )

    # Find the criterion (allow update of any criteria since they are shared)
    criterion = db.query(GeneralCriteria).filter(
        GeneralCriteria.id == actual_id
    ).first()

    if not criterion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Criterion not found"
        )

    # Update the criterion
    criterion.text = request.text
    db.commit()
    db.refresh(criterion)

    return GeneralCriteriaResponse(
        id=f"criteria_{criterion.id}",
        text=criterion.text,
        active=criterion.is_active
    )


@router.delete("/criteria/{criteria_id}")
async def delete_criteria(
    criteria_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Delete a criterion"""
    # Extract the actual ID from the criteria_id string
    try:
        actual_id = int(criteria_id.replace("criteria_", ""))
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid criteria ID format"
        )

    # Debug: Log the ID being searched
    print(f"DEBUG: Searching for criterion with ID: {actual_id}")
    print(f"DEBUG: Original criteria_id: {criteria_id}")

    # Find the criterion (allow deletion of any criteria since they are shared)
    criterion = db.query(GeneralCriteria).filter(
        GeneralCriteria.id == actual_id
    ).first()

    if not criterion:
        # Debug: Check if criterion exists with different query
        all_criteria = db.query(GeneralCriteria).all()
        print(f"DEBUG: All criteria IDs: {[c.id for c in all_criteria]}")
        print(f"DEBUG: Criterion with ID {actual_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Criterion not found"
        )

    # Delete the criterion
    db.delete(criterion)
    db.commit()

    return {"message": "Criterion deleted successfully"}


@router.post("/criteria/{criteria_id}/delete")
async def delete_criteria_post(
    criteria_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Delete criterion using POST method"""
    try:
        actual_id = int(criteria_id.replace("criteria_", ""))
    except ValueError:
        return {"error": "Invalid criteria ID format"}

    criterion = db.query(GeneralCriteria).filter(
        GeneralCriteria.id == actual_id
    ).first()

    if not criterion:
        return {"error": f"Criterion not found with ID {actual_id}"}

    db.delete(criterion)
    db.commit()

    return {"message": "Criterion deleted successfully", "deleted_id": actual_id}


@router.delete("/criteria-temp/{criteria_id}")
async def delete_criteria_temp(
    criteria_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Temporary delete criterion endpoint"""
    try:
        actual_id = int(criteria_id.replace("criteria_", ""))
    except ValueError:
        return {"error": "Invalid criteria ID format"}

    criterion = db.query(GeneralCriteria).filter(
        GeneralCriteria.id == actual_id
    ).first()

    if not criterion:
        return {"error": f"Criterion not found with ID {actual_id}"}

    db.delete(criterion)
    db.commit()

    return {"message": "Criterion deleted successfully", "deleted_id": actual_id}


@router.post("/criteria-simple/{criteria_id}/delete")
async def delete_criteria_simple(
    criteria_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Simple delete criterion endpoint"""
    try:
        actual_id = int(criteria_id.replace("criteria_", ""))
    except ValueError:
        return {"error": "Invalid criteria ID format"}

    criterion = db.query(GeneralCriteria).filter(
        GeneralCriteria.id == actual_id
    ).first()

    if not criterion:
        return {"error": f"Criterion not found with ID {actual_id}"}

    db.delete(criterion)
    db.commit()

    return {"message": "Criterion deleted successfully", "deleted_id": actual_id}


@router.get("/debug-direct")
async def debug_direct(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Direct database test"""
    try:
        # Test direct database access
        criterion = db.query(GeneralCriteria).filter(GeneralCriteria.id == 57).first()
        return {
            "criterion_57_found": criterion is not None,
            "criterion_57_text": criterion.text if criterion else None,
            "criterion_57_user_id": criterion.user_id if criterion else None,
            "total_criteria": db.query(GeneralCriteria).count()
        }
    except Exception as e:
        return {"error": str(e)}


@router.get("/debug-delete-test")
async def debug_delete_test(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Test DELETE logic directly"""
    try:
        # Test the exact logic from DELETE endpoint
        criteria_id = 'criteria_23'
        actual_id = int(criteria_id.replace('criteria_', ''))

        criterion = db.query(GeneralCriteria).filter(
            GeneralCriteria.id == actual_id
        ).first()

        if criterion:
            result = {
                "found": True,
                "id": criterion.id,
                "user_id": criterion.user_id,
                "text": criterion.text,
                "is_active": criterion.is_active
            }
        else:
            all_criteria = db.query(GeneralCriteria).all()
            all_ids = [c.id for c in all_criteria]
            result = {
                "found": False,
                "searched_id": actual_id,
                "available_ids": all_ids
            }

        return result
    except Exception as e:
        return {"error": str(e)}


@router.get("/debug-test")
async def debug_test(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Debug endpoint to verify if changes are applied"""
    # Test finding a criterion without user_id filter
    criterion = db.query(GeneralCriteria).filter(
        GeneralCriteria.id == 55
    ).first()

    return {
        "message": "Debug test successful",
        "criterion_found": criterion is not None,
        "criterion_text": criterion.text if criterion else None,
        "criterion_user_id": criterion.user_id if criterion else None,
        "current_user_id": current_user.id
    }


@router.get("/results/{analysis_id}", response_model=GeneralAnalysisResult)
async def get_general_analysis_result(
    analysis_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get general analysis result"""
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )

    # Check permissions
    if analysis.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    if not analysis.result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis result not available"
        )

    # Parse result into general analysis format
    criteria_results = []
    if analysis.result.issues:
        for issue in analysis.result.get_issues():
            criteria_results.append({
                "criterion": issue.get("criterion", "Unknown"),
                "assessment": issue.get("assessment", ""),
                "status": issue.get("status", "unknown"),
                "confidence": issue.get("confidence", 0.0),
                "evidence": issue.get("evidence", []),
                "recommendations": issue.get("recommendations", [])
            })

    return GeneralAnalysisResult(
        id=str(analysis.id),
        analysis_type="general",
        timestamp=analysis.created_at,
        overall_assessment=analysis.result.summary,
        criteria_results=criteria_results,
        token_usage={
            "total_tokens": analysis.result.tokens_used or 0,
            "prompt_tokens": analysis.result.tokens_used or 0,  # Placeholder
            "completion_tokens": 0  # Placeholder
        },
        processing_time=float(analysis.result.processing_time or 0),
        status=analysis.status
    )


@router.post("/analyze-selected")
async def analyze_selected_criteria(
    request: AnalyzeSelectedRequest,
    db: Session = Depends(get_db)
) -> Any:
    """Analyze selected criteria using LLM with dynamic prompt insertion"""
    try:
        print("="*50)
        print("DEBUG: NOVA REQUISICAO RECEBIDA")
        print(f"DEBUG: Starting analysis for criteria: {request.criteria_ids}")
        print(f"DEBUG: File paths: {request.file_paths}")
        print(f"DEBUG: Is reanalysis: {request.is_reanalysis}")
        print(f"DEBUG: Result ID to update: {request.result_id_to_update}")
        print(f"DEBUG: Analysis name: {request.analysis_name}")
        print(f"DEBUG: Request type: {type(request)}")
        print(f"DEBUG: Request dict: {request.__dict__ if hasattr(request, '__dict__') else 'No dict'}")
        print("="*50)

        # Get prompt service
        print("DEBUG: Getting prompt service...")
        prompt_service = get_prompt_service(db)

        # Step 1: Read the general prompt from database
        print("DEBUG: Getting general prompt from database...")
        try:
            general_prompt = prompt_service.get_general_prompt(7)  # Try the updated prompt with code structure
        except Exception as e:
            print(f"DEBUG: Error getting prompt 7, using default: {e}")
            general_prompt = prompt_service.get_general_prompt()  # Use default prompt
        print(f"DEBUG: Retrieved general prompt length: {len(general_prompt)}")

        # Step 2: Get selected criteria from database
        print("DEBUG: Getting selected criteria from database...")
        selected_criteria = prompt_service.get_selected_criteria(request.criteria_ids)
        print(f"DEBUG: Found {len(selected_criteria)} criteria")
        print(f"DEBUG: Requested criteria IDs: {request.criteria_ids}")

        if not selected_criteria:
            print(f"DEBUG: No valid criteria found for requested IDs: {request.criteria_ids}")
            print(f"DEBUG: Available criteria in database will be listed:")

            # Get available criteria for error message
            available_ids = []
            try:
                all_available = db.query(GeneralCriteria).filter(GeneralCriteria.is_active == True).all()
                available_ids = [f'criteria_{c.id}' for c in all_available]
                print(f"DEBUG: Available criteria: {[f'criteria_{c.id}: {c.text[:30]}...' for c in all_available]}")
            except Exception as e:
                print(f"DEBUG: Error logging available criteria: {e}")

            # Return a more informative error
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Nenhum critério válido encontrado para os IDs solicitados: {request.criteria_ids}. IDs disponíveis: {available_ids}"
            )

        # Step 3: Insert criteria into prompt (in memory only)
        modified_prompt = prompt_service.insert_criteria_into_prompt(general_prompt, selected_criteria)
        print(f"DEBUG: Modified prompt length: {len(modified_prompt)}")

        # Step 4: Read source code file and replace placeholder
        try:
            # Use the first file path from the request
            if not request.file_paths or len(request.file_paths) == 0:
                raise HTTPException(status_code=400, detail="Nenhum arquivo de código fonte fornecido")

            file_path = request.file_paths[0]  # Use first file path
            print(f"DEBUG: Reading source code from: {file_path}")

            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                source_code = f.read()
                print(f"DEBUG: Source code file read successfully: {len(source_code)} characters")

                # Sanitizar o conteúdo para remover caracteres problemáticos
                source_code = source_code.replace('\r\n', '\n')  # Normalizar line endings
                source_code = source_code.replace('\r', '\n')

                # Verificar e substituir caracteres problemáticos
                try:
                    source_code = source_code.encode('utf-8', errors='ignore').decode('utf-8')
                    print(f"DEBUG: Source code sanitized successfully")
                except Exception as sanitize_error:
                    print(f"DEBUG: Warning - could not fully sanitize source code: {sanitize_error}")

                print(f"DEBUG: Final source code length: {len(source_code)} characters")
        except Exception as e:
            print(f"DEBUG: Error reading source code file: {e}")
            raise HTTPException(status_code=500, detail=f"Erro ao ler arquivo de código fonte: {str(e)}")

        # Replace placeholder with actual source code
        final_prompt = modified_prompt.replace("[INSERIR CÓDIGO AQUI]", source_code)
        print(f"DEBUG: Replaced placeholder with source code")
        print(f"DEBUG: Final prompt length: {len(final_prompt)}")

        # Log do prompt completo para debug
        print("\n" + "="*80)
        print("PROMPT FINAL ENVIADO PARA A LLM:")
        print("="*80)
        print(final_prompt[:1000] + "..." if len(final_prompt) > 1000 else final_prompt)
        print("="*80)
        print("FIM DO PROMPT")
        print("="*80 + "\n")

        print(f"=== SENDING TO LLM SERVICE ===")
        print(f"DEBUG: About to send prompt of length {len(final_prompt)}")
        print(f"DEBUG: Temperature: {request.temperature}, Max tokens: {request.max_tokens}")

        # Increase max_tokens for multiple criteria to ensure complete analysis
        max_tokens = request.max_tokens
        if len(selected_criteria) > 2:
            max_tokens = max(max_tokens, 6000)  # Ensure at least 6000 tokens for 3+ criteria

        llm_response = await llm_service.send_prompt_with_end_detection(
            final_prompt,
            temperature=request.temperature,
            max_tokens=max_tokens
        )

        print("XXXXXXXXXX DEBUG: LLM response received XXXXXXXXXX")
        print(f"DEBUG: LLM response type: {type(llm_response)}")
        print(f"DEBUG: LLM response keys: {llm_response.keys() if isinstance(llm_response, dict) else 'Not a dict'}")
        print(f"DEBUG: Full LLM response: {llm_response}")

        llm_response_content = llm_response.get('response', '')
        print("YYYYYYYYYY DEBUG: Checking response content YYYYYYYYYY")
        print(f"DEBUG: LLM response['response'] type: {type(llm_response_content)}")
        print(f"DEBUG: LLM response['response'] length: {len(llm_response_content)}")
        print(f"DEBUG: LLM response['response'] preview: {llm_response_content[:200]}")
        print(f"DEBUG: Is response empty? {not llm_response_content}")
        print("ZZZZZZZZZ END LLM SERVICE DEBUG ZZZZZZZZZ")

        # Check if response is empty
        if not llm_response_content:
            print("ERROR: LLM response is empty!")
            extracted_content = {"criteria_results": {}, "raw_response": ""}
        else:
            # Step 7: Extract content from LLM response
            print(f"=== RAW LLM RESPONSE FOR DEBUG ===")
            print(f"Content type: {type(llm_response_content)}")
            print(f"Content length: {len(llm_response_content)}")
            print(f"Content preview: {llm_response_content[:500]}")
            print(f"=== END RAW LLM RESPONSE ===")

            # DEBUG: Test if response contains expected patterns
            print(f"=== DEBUG RESPONSE PATTERNS ===")
            print(f"Contains 'Critério': {'Critério' in llm_response_content}")
            print(f"Contains '##': {'##' in llm_response_content}")
            print(f"Contains 'Status:': {'Status:' in llm_response_content}")
            print(f"Contains 'Confiança': {'Confiança' in llm_response_content}")
            print(f"=== END DEBUG PATTERNS ===")

            print(f"DEBUG: About to call extract_markdown_content with response of length {len(llm_response_content)}")
            extracted_content = llm_service.extract_markdown_content(llm_response_content)
            print(f"DEBUG: extract_markdown_content returned: {type(extracted_content)}")
            print(f"DEBUG: extracted_content keys: {extracted_content.keys() if isinstance(extracted_content, dict) else 'Not a dict'}")
            print(f"DEBUG: criteria_results in extracted_content: {extracted_content.get('criteria_results', {}) if isinstance(extracted_content, dict) else 'N/A'}")

            # DEBUG: Show criteria_results details
            if isinstance(extracted_content, dict) and 'criteria_results' in extracted_content:
                criteria_results = extracted_content['criteria_results']
                print(f"DEBUG: criteria_results type: {type(criteria_results)}")
                print(f"DEBUG: criteria_results content: {criteria_results}")
                print(f"DEBUG: criteria_results empty: {not criteria_results}")
                if isinstance(criteria_results, dict):
                    print(f"DEBUG: criteria_results keys: {list(criteria_results.keys())}")
                    for key, value in criteria_results.items():
                        print(f"DEBUG: {key}: {type(value)} - {str(value)[:100] if value else 'None'}")

            # Step 7.5: For single criterion analysis, ensure only the requested criterion is returned
            print(f"DEBUG: Starting criteria filtering...")
            print(f"DEBUG: Selected criteria: {selected_criteria}")
            print(f"DEBUG: Request criteria IDs: {request.criteria_ids}")
            print(f"DEBUG: Extracted criteria results: {extracted_content.get('criteria_results', {}).keys()}")

            # For single criterion analysis, force filtering to return ONLY the requested criterion
            if len(selected_criteria) == 1 and len(request.criteria_ids) == 1:
                requested_criteria_id = request.criteria_ids[0]
                target_criteria_id = requested_criteria_id.replace("criteria_", "")
                target_criteria_name = selected_criteria[0].text.strip()

                print(f"DEBUG: Single criterion analysis - FORCING filter for ID: {target_criteria_id}, Name: {target_criteria_name}")
                print(f"DEBUG: Is reanalysis: {request.is_reanalysis}")
                print(f"DEBUG: Original criteria_results count: {len(extracted_content.get('criteria_results', {}))}")

                # Always create a result with only the requested criterion
                forced_criteria_results = {}

                # First, try exact ID match
                if f"criteria_{target_criteria_id}" in extracted_content.get("criteria_results", {}):
                    forced_criteria_results[f"criteria_{target_criteria_id}"] = extracted_content["criteria_results"][f"criteria_{target_criteria_id}"]
                    print(f"DEBUG: Found exact ID match for criteria_{target_criteria_id}")
                else:
                    # For reanalysis, we need to be more strict about filtering
                    # Even if LLM returns multiple criteria, we only want the requested one
                    best_match = None
                    best_similarity_score = 0

                    for extracted_key, result_data in extracted_content.get("criteria_results", {}).items():
                        result_name = result_data.get("name", "").strip().lower()
                        target_name_lower = target_criteria_name.lower()

                        print(f"DEBUG: Comparing '{result_name}' with '{target_name_lower}'")

                        # Calculate similarity score with stricter criteria for reanalysis
                        similarity_score = 0
                        if result_name == target_name_lower:
                            similarity_score = 100
                        elif target_name_lower in result_name and len(result_name) - len(target_name_lower) < 20:
                            similarity_score = 90
                        elif result_name in target_name_lower and len(target_name_lower) - len(result_name) < 20:
                            similarity_score = 85
                        elif "princípio" in target_name_lower.lower() and "princípio" in result_name.lower():
                            # For principles, try to match by principle name
                            target_principle = target_name_lower.replace("princípio", "").replace("principle", "").strip()
                            result_principle = result_name.replace("princípio", "").replace("principle", "").strip()
                            if target_principle and result_principle and (
                                target_principle in result_principle or result_principle in target_principle
                            ):
                                similarity_score = 80
                        elif any(word in result_name for word in target_name_lower.split() if len(word) > 3):
                            similarity_score = 60

                        if similarity_score > best_similarity_score:
                            best_similarity_score = similarity_score
                            best_match = result_data
                            print(f"DEBUG: New best match: '{result_name}' with score {similarity_score}")

                    print(f"DEBUG: Best similarity score: {best_similarity_score}")

                    # For reanalysis, require higher similarity threshold
                    required_similarity = 70 if request.is_reanalysis else 40

                    if best_match and best_similarity_score >= required_similarity:
                        forced_criteria_results[f"criteria_{target_criteria_id}"] = best_match
                        print(f"DEBUG: Using best match with score {best_similarity_score}")
                    else:
                        # If no good match found, create a result for the requested criterion
                        if request.is_reanalysis:
                            forced_criteria_results[f"criteria_{target_criteria_id}"] = {
                                "name": target_criteria_name,
                                "content": f"**Status:** Não Conforme\n**Confiança:** 1.0\n\nReanálise do critério solicitado. O sistema não encontrou uma análise específica para este critério nos resultados retornados pelo LLM.\n\nCritério analisado: {target_criteria_name}"
                            }
                        else:
                            forced_criteria_results[f"criteria_{target_criteria_id}"] = {
                                "name": target_criteria_name,
                                "content": "**Status:** Não Conforme\n**Confiança:** 1.0\n\nAnálise não disponível. O critério solicitado não foi encontrado nos resultados gerados pelo LLM."
                            }
                        print(f"DEBUG: No good match found, creating {'reanalysis' if request.is_reanalysis else 'empty'} result for {target_criteria_name}")

                # ALWAYS replace with our forced single result
                extracted_content["criteria_results"] = forced_criteria_results
                print(f"DEBUG: FORCED single criterion result: {forced_criteria_results}")
                print(f"DEBUG: Total criteria in final result: {len(forced_criteria_results)}")
                print(f"DEBUG: Final criteria_results keys: {list(forced_criteria_results.keys())}")
            else:
                # For multiple criteria, use the original mapping logic
                # Create mapping from criteria name to criteria ID
                criteria_name_to_id = {}
                for criteria in selected_criteria:
                    criteria_name_to_id[criteria.text.strip().lower()] = criteria.id
                    print(f"DEBUG: Mapping '{criteria.text.strip().lower()}' to ID {criteria.id}")

                # Remap criteria_results to use actual criteria IDs
                remapped_criteria_results = {}
                for extracted_key, result_data in extracted_content.get("criteria_results", {}).items():
                    result_name = result_data.get("name", "").strip().lower()

                    if result_name in criteria_name_to_id:
                        criteria_id = criteria_name_to_id[result_name]
                        remapped_criteria_results[f"criteria_{criteria_id}"] = result_data
                        print(f"DEBUG: Found exact match - mapped to criteria_{criteria_id}")
                    else:
                        # Try fuzzy matching
                        found_match = False
                        for criteria_text, candidate_id in criteria_name_to_id.items():
                            if (result_name in criteria_text or criteria_text in result_name or
                                result_name.split(':')[0].strip() in criteria_text or
                                criteria_text.split(':')[0].strip() in result_name):
                                remapped_criteria_results[f"criteria_{candidate_id}"] = result_data
                                print(f"DEBUG: Found fuzzy match - mapped '{result_name}' to criteria_{candidate_id}")
                                found_match = True
                                break

                        if not found_match:
                            # Keep original key if no match found
                            remapped_criteria_results[extracted_key] = result_data
                            print(f"DEBUG: No match found for '{result_name}', keeping original key")

                extracted_content["criteria_results"] = remapped_criteria_results

        # Step 8: Save analysis results to database
        import json
        from datetime import datetime
        import time

        print("DEBUG: Starting database save process...")

        # Calculate processing time
        processing_start = time.time()
        processing_time = f"{time.time() - processing_start:.2f}s"

        try:
            # Check if this is a reanalysis
            if request.is_reanalysis and request.result_id_to_update:
                print(f"DEBUG: Updating existing analysis result with ID: {request.result_id_to_update}")
                # Find existing result
                db_analysis_result = db.query(GeneralAnalysisResultModel).filter(
                    GeneralAnalysisResultModel.id == request.result_id_to_update
                ).first()

                if db_analysis_result:
                    # Update existing record - merge new criteria with existing ones
                    existing_criteria = db_analysis_result.criteria_results or {}
                    new_criteria = extracted_content.get("criteria_results", {})
                    # Merge: update existing criteria with new results
                    existing_criteria.update(new_criteria)
                    db_analysis_result.criteria_results = existing_criteria
                    db_analysis_result.raw_response = extracted_content.get("raw_response", "")
                    db_analysis_result.model_used = llm_response.get("model", "claude-3-sonnet-20240229")
                    db_analysis_result.usage = llm_response.get("usage", {})
                    db_analysis_result.modified_prompt = modified_prompt
                    db_analysis_result.processing_time = processing_time

                    print("DEBUG: Updating existing record...")
                    db.commit()
                    print(f"DEBUG: Successfully updated analysis result with ID: {db_analysis_result.id}")
                else:
                    print(f"DEBUG: Result with ID {request.result_id_to_update} not found, creating new record")
                    request.is_reanalysis = False  # Force creation of new record
                    request.result_id_to_update = None

            if not request.is_reanalysis or not request.result_id_to_update:
                print("DEBUG: Creating new GeneralAnalysisResult record...")
                # Create new GeneralAnalysisResult record
                db_analysis_result = GeneralAnalysisResultModel(
                    analysis_name=request.analysis_name,
                    criteria_count=len(selected_criteria),
                    user_id=1,  # Using fixed user_id for testing (should be current_user.id)
                    criteria_results=extracted_content.get("criteria_results", {}),
                    raw_response=extracted_content.get("raw_response", ""),
                    model_used=llm_response.get("model", "claude-3-sonnet-20240229"),
                    usage=llm_response.get("usage", {}),
                    file_paths=json.dumps(request.file_paths),
                    modified_prompt=modified_prompt,
                    processing_time=processing_time
                )

                print("DEBUG: Adding record to session...")
                db.add(db_analysis_result)

                print("DEBUG: Committing transaction...")
                db.commit()

                print("DEBUG: Refreshing record...")
                db.refresh(db_analysis_result)

                print(f"DEBUG: Successfully saved analysis result to database with ID: {db_analysis_result.id}")

        except Exception as db_error:
            print(f"DEBUG: Database save failed: {db_error}")
            import traceback
            traceback.print_exc()
            # Don't re-raise - continue with returning the result to the user
            db_analysis_result = None

        # Step 9: Create analysis result structure
        result_data = {
            "success": True,
            "analysis_name": request.analysis_name,
            "criteria_count": len(selected_criteria),
            "timestamp": llm_response["timestamp"],
            "model_used": llm_response["model"],
            "usage": llm_response["usage"],
            "criteria_results": extracted_content.get("criteria_results", {}),
            "raw_response": extracted_content.get("raw_response", ""),
            "debug_raw_llm_response": llm_response_content,  # For debugging
            "modified_prompt": modified_prompt,
            "file_paths": request.file_paths,
            "saved_to_db": True,
            "db_result_id": db_analysis_result.id
        }

        return result_data

    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR in analyze_selected_criteria: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing selected criteria: {str(e)}"
        )


@router.get("/results")
async def get_analysis_results(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get all analysis results for the current user"""
    try:
        # Get all analysis results for the user
        results = db.query(GeneralAnalysisResultModel).filter(
            GeneralAnalysisResultModel.user_id == current_user.id
        ).order_by(GeneralAnalysisResultModel.created_at.desc()).all()

        # Convert to response format
        formatted_results = []
        for result in results:
            formatted_results.append({
                "id": result.id,
                "analysis_name": result.analysis_name,
                "criteria_count": result.criteria_count,
                "timestamp": result.created_at,
                "model_used": result.model_used,
                "processing_time": result.processing_time,
                "file_paths": result.get_file_paths(),
                "criteria_results": result.get_criteria_results(),
                "raw_response": result.raw_response,
                "usage": result.get_usage()
            })

        return {
            "success": True,
            "results": formatted_results,
            "total": len(formatted_results)
        }

    except Exception as e:
        print(f"ERROR in get_analysis_results: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving analysis results: {str(e)}"
        )


@router.get("/debug-test-public")
async def test_endpoint() -> Any:
    """Simple test endpoint"""
    return {"message": "Test endpoint works", "status": "ok"}


@router.get("/criteria-working")
async def get_criteria_working(
    db: Session = Depends(get_db)
) -> Any:
    """Get all criteria (working public endpoint)"""
    try:
        # Get all active criteria from database
        all_criteria = db.query(GeneralCriteria).filter(
            GeneralCriteria.is_active == True
        ).order_by(GeneralCriteria.order, GeneralCriteria.created_at).all()

        # Convert to response format
        result = []
        for criterion in all_criteria:
            result.append({
                "id": f"criteria_{criterion.id}",
                "text": criterion.text,
                "active": criterion.is_active
            })

        return result

    except Exception as e:
        print(f"ERROR in get_criteria_working: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving criteria: {str(e)}"
        )


@router.get("/criteria_public_test")
async def get_criteria_public_test(
    db: Session = Depends(get_db)
) -> Any:
    """Alternative test endpoint without hyphen"""
    try:
        # Get all active criteria from database
        all_criteria = db.query(GeneralCriteria).filter(
            GeneralCriteria.is_active == True
        ).order_by(GeneralCriteria.order, GeneralCriteria.created_at).all()

        # Convert to response format
        result = []
        for criterion in all_criteria:
            result.append({
                "id": f"criteria_{criterion.id}",
                "text": criterion.text,
                "active": criterion.is_active
            })

        return result

    except Exception as e:
        print(f"ERROR in get_criteria_public_test: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving criteria: {str(e)}"
        )


@router.get("/results-public")
async def get_analysis_results_public(
    db: Session = Depends(get_db)
) -> Any:
    """Get all analysis results (public endpoint for testing)"""
    try:
        # Get all analysis results for user_id = 1 (testing)
        results = db.query(GeneralAnalysisResultModel).filter(
            GeneralAnalysisResultModel.user_id == 1
        ).order_by(GeneralAnalysisResultModel.created_at.desc()).all()

        # Convert to response format
        formatted_results = []
        for result in results:
            formatted_results.append({
                "id": result.id,
                "analysis_name": result.analysis_name,
                "criteria_count": result.criteria_count,
                "timestamp": result.created_at,
                "model_used": result.model_used,
                "processing_time": result.processing_time,
                "file_paths": result.get_file_paths(),
                "criteria_results": result.get_criteria_results(),
                "raw_response": result.raw_response,
                "usage": result.get_usage()
            })

        return {
            "success": True,
            "results": formatted_results,
            "total": len(formatted_results)
        }

    except Exception as e:
        print(f"ERROR in get_analysis_results_public: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving analysis results: {str(e)}"
        )


@router.get("/results/{result_id}")
async def get_analysis_result(
    result_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get a specific analysis result by ID"""
    try:
        # Get the analysis result
        result = db.query(GeneralAnalysisResultModel).filter(
            GeneralAnalysisResultModel.id == result_id,
            GeneralAnalysisResultModel.user_id == current_user.id
        ).first()

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Analysis result not found"
            )

        return {
            "success": True,
            "result": {
                "id": result.id,
                "analysis_name": result.analysis_name,
                "criteria_count": result.criteria_count,
                "timestamp": result.created_at,
                "model_used": result.model_used,
                "processing_time": result.processing_time,
                "file_paths": result.get_file_paths(),
                "criteria_results": result.get_criteria_results(),
                "raw_response": result.raw_response,
                "usage": result.get_usage(),
                "modified_prompt": result.modified_prompt
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR in get_analysis_result: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving analysis result: {str(e)}"
        )


# Endpoint para atualizar resultados - Updated
@router.put("/results/{result_id}/update", response_model=dict)
async def update_analysis_result(
    result_id: int,
    update_data: AnalysisResultUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Update a specific analysis result"""
    print(f"DEBUG: ENDPOINT DE ATUALIZAÇÃO CHAMADO! result_id={result_id}, user_id={current_user.id}")
    print(f"DEBUG: update_data recebido: {update_data}")
    try:
        # Get the analysis result
        result = db.query(GeneralAnalysisResultModel).filter(
            GeneralAnalysisResultModel.id == result_id,
            GeneralAnalysisResultModel.user_id == current_user.id
        ).first()

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Analysis result not found"
            )

        # Get current criteria results
        criteria_results = result.get_criteria_results()

        # Update specific criteria if provided
        criteria_key = update_data.criteria_key
        if criteria_key in criteria_results:
            criteria_results[criteria_key] = {
                **criteria_results[criteria_key],
                **update_data.criteria_data
            }
            # Forçar refresh do objeto para evitar conflitos com o ORM
            db.refresh(result)

            # Usar SQL direto para atualização (último recurso)
            import json
            from sqlalchemy import text

            # Obter o JSON atualizado como string
            updated_json = json.dumps(criteria_results)

            print(f"DEBUG: JSON atualizado como string tem {len(updated_json)} caracteres")

            # Executar atualização SQL direta
            sql_query = text("""
                UPDATE general_analysis_results
                SET criteria_results = :criteria_results,
                    updated_at = NOW()
                WHERE id = :result_id AND user_id = :user_id
            """)

            print(f"DEBUG: Executando SQL direto:")
            print(f"DEBUG: SQL Query: {sql_query}")
            print(f"DEBUG: Parâmetros: criteria_results length={len(updated_json)}, result_id={result_id}, user_id={current_user.id}")

            db.execute(sql_query, {
                'criteria_results': updated_json,
                'result_id': result_id,
                'user_id': current_user.id
            })

            print(f"DEBUG: SQL executado, fazendo commit...")
            db.commit()
            print(f"DEBUG: Commit realizado com sucesso!")

            # Verificação adicional - consultar o banco diretamente
            from sqlalchemy import text
            verify_query = text("SELECT criteria_results FROM general_analysis_results WHERE id = :result_id")
            verify_result = db.execute(verify_query, {'result_id': result_id}).fetchone()
            if verify_result:
                stored_json = verify_result[0]
                print(f"DEBUG: Verificação pós-commit: Dados armazenados no banco têm {len(stored_json)} caracteres")
                import json
                try:
                    stored_data = json.loads(stored_json)
                    if criteria_key in stored_data:
                        print(f"DEBUG: Verificação pós-commit: {criteria_key} encontrado nos dados armazenados!")
                        print(f"DEBUG: Conteúdo armazenado: {stored_data[criteria_key].get('content', 'NÃO ENCONTRADO')[:100]}...")
                    else:
                        print(f"DEBUG: Verificação pós-commit: {criteria_key} NÃO encontrado nos dados armazenados!")
                except json.JSONDecodeError as e:
                    print(f"DEBUG: Erro ao decodificar JSON armazenado: {e}")
            else:
                print(f"DEBUG: Verificação pós-commit: Nenhum dado encontrado para result_id={result_id}")

            # Forçar refresh do objeto
            db.refresh(result)
            print(f"DEBUG: Objeto refresh realizado")

            # Verificar se o objeto foi atualizado
            refreshed_criteria = result.get_criteria_results()
            print(f"DEBUG: Conteúdo após refresh: {refreshed_criteria.get(criteria_key, {}).get('content', 'NÃO ENCONTRADO')[:100]}...")

            return {
                "success": True,
                "message": f"Criteria {criteria_key} updated successfully",
                "updated_criteria": criteria_results[criteria_key]
            }
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR in update_analysis_result: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating analysis result: {str(e)}"
        )


# Endpoint temporário para teste sem autenticação
@router.put("/results/{result_id}/update-test", response_model=dict)
async def update_analysis_result_test(
    result_id: int,
    update_data: AnalysisResultUpdate,
    db: Session = Depends(get_db)
) -> Any:
    """Update a specific analysis result - TEMPORÁRIO SEM AUTH"""
    try:
        # Get the analysis result (sem verificação de usuário)
        result = db.query(GeneralAnalysisResultModel).filter(
            GeneralAnalysisResultModel.id == result_id
        ).first()

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Analysis result not found"
            )

        # Get current criteria results
        criteria_results = result.get_criteria_results()

        # Update specific criteria if provided
        criteria_key = update_data.criteria_key
        if criteria_key in criteria_results:
            criteria_results[criteria_key] = {
                **criteria_results[criteria_key],
                **update_data.criteria_data
            }

            # Forçar refresh do objeto para evitar conflitos com o ORM
            db.refresh(result)

            # Usar SQL direto para atualização (último recurso)
            import json
            from sqlalchemy import text

            # Obter o JSON atualizado como string
            updated_json = json.dumps(criteria_results)

            print(f"DEBUG: JSON atualizado como string tem {len(updated_json)} caracteres (endpoint de teste)")

            # Executar atualização SQL direta
            sql_query = text("""
                UPDATE general_analysis_results
                SET criteria_results = :criteria_results,
                    updated_at = NOW()
                WHERE id = :result_id
            """)

            db.execute(sql_query, {
                'criteria_results': updated_json,
                'result_id': result_id
            })

            db.commit()

            # Forçar refresh do objeto
            db.refresh(result)

            print(f"DEBUG: Atualização SQL direta executada (endpoint de teste)")

            return {
                "success": True,
                "message": f"Criteria {criteria_key} updated successfully (TEST)",
                "updated_criteria": criteria_results[criteria_key]
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Criteria {criteria_key} not found in analysis result"
            )

    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR in update_analysis_result_test: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating analysis result: {str(e)}"
        )


@router.put("/results/{analysis_id}/manual", response_model=GeneralAnalysisResult)
async def update_manual_result(
    analysis_id: int,
    result_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Update analysis result manually"""
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )

    # Check permissions
    if analysis.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    if not analysis.result:
        # Create manual result
        from app.models.analysis import AnalysisResult
        manual_result = AnalysisResult(
            analysis_id=analysis.id,
            summary=result_data.get("overall_assessment", ""),
            detailed_findings="Manual analysis result",
            recommendations=result_data.get("recommendations", ""),
            confidence=result_data.get("confidence", 1.0),
            model_used="manual",
            tokens_used=0,
            processing_time="0.0",
            quality_score=result_data.get("score", 0),
            issues=result_data.get("criteria_results", [])
        )
        db.add(manual_result)
    else:
        # Update existing result
        analysis.result.summary = result_data.get("overall_assessment", analysis.result.summary)
        analysis.result.confidence = result_data.get("confidence", analysis.result.confidence)
        analysis.result.quality_score = result_data.get("score", analysis.result.quality_score)
        analysis.result.issues = result_data.get("criteria_results", analysis.result.issues)
        analysis.result.model_used = "manual"

    db.commit()
    db.refresh(analysis)

    # Return updated result
    return await get_general_analysis_result(analysis_id, current_user, db)



@router.delete("/results/{result_id}")
async def delete_analysis_result(
    result_id: int,
    db: Session = Depends(get_db)
) -> Any:
    """Delete a specific analysis result"""
    try:
        # Find the analysis result
        result = db.query(GeneralAnalysisResultModel).filter(
            GeneralAnalysisResultModel.id == result_id
        ).first()

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Analysis result not found"
            )

        # Delete the result
        db.delete(result)
        db.commit()

        return {
            "success": True,
            "message": f"Analysis result {result_id} deleted successfully",
            "deleted_id": result_id
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR in delete_analysis_result: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting analysis result: {str(e)}"
        )




@router.delete("/results")
async def delete_multiple_analysis_results(
    request: dict,
    db: Session = Depends(get_db)
) -> Any:
    """Delete multiple analysis results"""
    try:
        result_ids = request.get("result_ids", [])

        if not result_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No result IDs provided"
            )

        # Find and delete the results
        deleted_count = 0
        for result_id in result_ids:
            result = db.query(GeneralAnalysisResultModel).filter(
                GeneralAnalysisResultModel.id == result_id
            ).first()
            
            if result:
                db.delete(result)
                deleted_count += 1

        db.commit()

        return {
            "success": True,
            "message": f"Successfully deleted {deleted_count} analysis results",
            "deleted_count": deleted_count,
            "requested_ids": result_ids
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR in delete_multiple_analysis_results: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting analysis results: {str(e)}"
        )



