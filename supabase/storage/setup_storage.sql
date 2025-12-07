-- AVALIA Supabase Storage Setup
-- This script sets up storage buckets and policies for file uploads

-- Create storage buckets for different file types
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
    'code-files',
    'code-files',
    false,
    104857600, -- 100MB
    ARRAY['text/plain', 'text/x-python', 'text/javascript', 'application/javascript', 'text/x-typescript',
          'text/x-java', 'text/x-c', 'text/x-c++', 'text/x-csharp', 'text/x-go', 'text/x-rust',
          'text/x-ruby', 'text/x-php', 'text/x-swift', 'text/x-kotlin', 'text/x-scala',
          'text/html', 'text/css', 'text/scss', 'text/less', 'application/json', 'application/xml',
          'text/x-yaml', 'text/x-toml', 'text/x-ini', 'text/markdown']
) ON CONFLICT (id) DO NOTHING;

INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
    'analysis-reports',
    'analysis-reports',
    false,
    52428800, -- 50MB
    ARRAY['application/pdf', 'text/plain', 'application/json', 'text/csv']
) ON CONFLICT (id) DO NOTHING;

INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
    'user-avatars',
    'user-avatars',
    true,
    2097152, -- 2MB
    ARRAY['image/jpeg', 'image/png', 'image/gif', 'image/webp']
) ON CONFLICT (id) DO NOTHING;

-- Create storage policies for code-files bucket
CREATE POLICY "Users can upload their own code files" ON storage.objects
FOR INSERT WITH CHECK (
    bucket_id = 'code-files' AND
    auth.role() = 'authenticated' AND
    (storage.foldername(name))[1] = auth.uid()::text
);

CREATE POLICY "Users can view their own code files" ON storage.objects
FOR SELECT USING (
    bucket_id = 'code-files' AND
    (storage.foldername(name))[1] = auth.uid()::text
);

CREATE POLICY "Users can update their own code files" ON storage.objects
FOR UPDATE USING (
    bucket_id = 'code-files' AND
    (storage.foldername(name))[1] = auth.uid()::text
);

CREATE POLICY "Users can delete their own code files" ON storage.objects
FOR DELETE USING (
    bucket_id = 'code-files' AND
    (storage.foldername(name))[1] = auth.uid()::text
);

-- Create storage policies for analysis-reports bucket
CREATE POLICY "Users can upload their own analysis reports" ON storage.objects
FOR INSERT WITH CHECK (
    bucket_id = 'analysis-reports' AND
    auth.role() = 'authenticated' AND
    (storage.foldername(name))[1] = auth.uid()::text
);

CREATE POLICY "Users can view their own analysis reports" ON storage.objects
FOR SELECT USING (
    bucket_id = 'analysis-reports' AND
    (storage.foldername(name))[1] = auth.uid()::text
);

CREATE POLICY "Admins can view all analysis reports" ON storage.objects
FOR SELECT USING (
    bucket_id = 'analysis-reports' AND
    EXISTS (
        SELECT 1 FROM public.profiles
        WHERE id = auth.uid() AND is_admin = true
    )
);

CREATE POLICY "Users can update their own analysis reports" ON storage.objects
FOR UPDATE USING (
    bucket_id = 'analysis-reports' AND
    (storage.foldername(name))[1] = auth.uid()::text
);

CREATE POLICY "Users can delete their own analysis reports" ON storage.objects
FOR DELETE USING (
    bucket_id = 'analysis-reports' AND
    (storage.foldername(name))[1] = auth.uid()::text
);

-- Create storage policies for user-avatars bucket (public)
CREATE POLICY "Anyone can view avatars" ON storage.objects
FOR SELECT USING (bucket_id = 'user-avatars');

CREATE POLICY "Users can upload their own avatar" ON storage.objects
FOR INSERT WITH CHECK (
    bucket_id = 'user-avatars' AND
    auth.role() = 'authenticated' AND
    (storage.foldername(name))[1] = auth.uid()::text
);

CREATE POLICY "Users can update their own avatar" ON storage.objects
FOR UPDATE USING (
    bucket_id = 'user-avatars' AND
    (storage.foldername(name))[1] = auth.uid()::text
);

CREATE POLICY "Users can delete their own avatar" ON storage.objects
FOR DELETE USING (
    bucket_id = 'user-avatars' AND
    (storage.foldername(name))[1] = auth.uid()::text
);

-- Create function to get file URL
CREATE OR REPLACE FUNCTION public.get_file_url(bucket_name text, file_path text)
RETURNS text AS $$
BEGIN
    RETURN
        'https://' ||
        current_setting('app.supabase_url', true) ||
        '/storage/v1/object/public/' ||
        bucket_name || '/' ||
        file_path;
EXCEPTION
    WHEN OTHERS THEN
        RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Create function to check if user has access to file
CREATE OR REPLACE FUNCTION public.user_can_access_file(file_id text)
RETURNS boolean AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM public.uploaded_files uf
        WHERE uf.file_id = file_id
        AND (uf.user_id = auth.uid() OR uf.is_public = true OR
             EXISTS (
                 SELECT 1 FROM public.profiles p
                 WHERE p.id = auth.uid() AND p.is_admin = true
             ))
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create function to generate unique file path
CREATE OR REPLACE FUNCTION public.generate_file_path(user_id uuid, original_name text)
RETURNS text AS $$
DECLARE
    file_extension text;
    sanitized_name text;
    unique_id text;
BEGIN
    -- Extract file extension
    file_extension := SUBSTRING(original_name FROM '\.[^.]+$');

    -- Sanitize filename
    sanitized_name := REGEXP_REPLACE(
        LOWER(original_name),
        '[^a-z0-9\-_]',
        '_',
        'g'
    );

    -- Remove extension from sanitized name
    sanitized_name := REGEXP_REPLACE(sanitized_name, '\.[^.]+$', '');

    -- Generate unique identifier
    unique_id := SUBSTRING(encode(gen_random_bytes(8), 'hex'), 1, 8);

    -- Return path: user_id/timestamp_unique_id_sanitized_name.extension
    RETURN user_id::text || '/' ||
           EXTRACT(epoch FROM now())::text || '_' ||
           unique_id || '_' ||
           sanitized_name ||
           COALESCE(file_extension, '');
END;
$$ LANGUAGE plpgsql;

-- Create trigger to automatically generate file path for uploaded files
CREATE OR REPLACE FUNCTION public.handle_uploaded_file_path()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.file_path IS NULL OR NEW.file_path = '' THEN
        NEW.file_path := public.generate_file_path(NEW.user_id, NEW.original_name);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_handle_uploaded_file_path
    BEFORE INSERT ON public.uploaded_files
    FOR EACH ROW EXECUTE FUNCTION public.handle_uploaded_file_path();