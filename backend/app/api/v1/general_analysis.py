"""
General analysis endpoints for VerificAI Backend - STO-007
"""

from typing import List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.analysis import Analysis, AnalysisStatus
from app.models.prompt import Prompt, PromptCategory
from app.schemas.analysis import AnalysisCreate, AnalysisResponse
from app.api.v1.analysis import process_analysis

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


class GeneralCriteria(BaseModel):
    """Criteria model for general analysis"""
    id: str
    text: str
    active: bool = True


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


@router.get("/criteria", response_model=List[GeneralCriteria])
async def get_user_criteria(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get user's criteria from their general analysis prompts"""
    # Get user's general prompts
    general_prompts = db.query(Prompt).filter(
        Prompt.author_id == current_user.id,
        Prompt.category == PromptCategory.GENERAL
    ).all()

    criteria = []
    criteria_id = 0

    for prompt in general_prompts:
        # Extract criteria from prompt content
        lines = prompt.content.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('- '):
                criteria.append(GeneralCriteria(
                    id=f"criteria_{criteria_id}",
                    text=line[2:],  # Remove '- ' prefix
                    active=True
                ))
                criteria_id += 1

    return criteria


@router.post("/criteria", response_model=GeneralCriteria)
async def create_criteria(
    text: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Create a new criterion"""
    # Get or create user's general prompt
    general_prompt = db.query(Prompt).filter(
        Prompt.name == "General Analysis",
        Prompt.category == PromptCategory.GENERAL,
        Prompt.author_id == current_user.id
    ).first()

    if not general_prompt:
        # Create new general prompt
        prompt_content = f"You are a code quality expert. Analyze the provided code based on the following criteria:\n\n- {text}\n\n..."
        general_prompt = Prompt(
            name="General Analysis",
            content=prompt_content,
            category=PromptCategory.GENERAL,
            author_id=current_user.id,
            is_public=False
        )
        db.add(general_prompt)
    else:
        # Add criterion to existing prompt
        if 'criteria:' in general_prompt.content:
            # Insert after criteria section
            parts = general_prompt.content.split('criteria:')
            general_prompt.content = parts[0] + 'criteria:\n- ' + text + '\n' + parts[1]
        else:
            # Add to end
            general_prompt.content += f"\n- {text}"

    db.commit()
    db.refresh(general_prompt)

    return GeneralCriteria(
        id=f"criteria_{general_prompt.id}",
        text=text,
        active=True
    )


@router.put("/criteria/{criteria_id}", response_model=GeneralCriteria)
async def update_criteria(
    criteria_id: str,
    text: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Update an existing criterion"""
    # Find the criterion in user's prompts
    general_prompts = db.query(Prompt).filter(
        Prompt.author_id == current_user.id,
        Prompt.category == PromptCategory.GENERAL
    ).all()

    for prompt in general_prompts:
        if f"- {text}" not in prompt.content:
            continue

        # Replace the criterion
        old_text = None
        lines = prompt.content.split('\n')
        for i, line in enumerate(lines):
            if line.strip().startswith('- '):
                if f"criteria_{prompt.id}_{i}" == criteria_id:
                    old_text = line
                    break

        if old_text:
            prompt.content = prompt.content.replace(old_text, f"- {text}")
            db.commit()
            return GeneralCriteria(
                id=criteria_id,
                text=text,
                active=True
            )

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Criterion not found"
    )


@router.delete("/criteria/{criteria_id}")
async def delete_criteria(
    criteria_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Delete a criterion"""
    # Find and remove the criterion from user's prompts
    general_prompts = db.query(Prompt).filter(
        Prompt.author_id == current_user.id,
        Prompt.category == PromptCategory.GENERAL
    ).all()

    for prompt in general_prompts:
        lines = prompt.content.split('\n')
        for i, line in enumerate(lines):
            if line.strip().startswith('- '):
                if f"criteria_{prompt.id}_{i}" == criteria_id:
                    # Remove this line
                    lines.pop(i)
                    prompt.content = '\n'.join(lines)
                    db.commit()
                    return {"message": "Criterion deleted successfully"}

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Criterion not found"
    )


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