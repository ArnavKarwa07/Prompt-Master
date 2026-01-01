# Supabase Storage Bucket Policies
# Run these in the Supabase Dashboard under Storage > Policies

## Bucket: user-files

### Policy 1: Users can upload to their own folder
```sql
CREATE POLICY "Users can upload to own folder" ON storage.objects
FOR INSERT 
WITH CHECK (
    bucket_id = 'user-files' 
    AND auth.uid()::text = (storage.foldername(name))[1]
);
```

### Policy 2: Users can view their own files
```sql
CREATE POLICY "Users can view own files" ON storage.objects
FOR SELECT 
USING (
    bucket_id = 'user-files' 
    AND auth.uid()::text = (storage.foldername(name))[1]
);
```

### Policy 3: Users can delete their own files
```sql
CREATE POLICY "Users can delete own files" ON storage.objects
FOR DELETE 
USING (
    bucket_id = 'user-files' 
    AND auth.uid()::text = (storage.foldername(name))[1]
);
```

## Setup Instructions

1. Go to Supabase Dashboard > Storage
2. Create a new bucket called `user-files`
3. Keep it as a **private** bucket (not public)
4. Go to Policies tab and add the above policies
