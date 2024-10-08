from storages.backends.s3boto3 import S3Boto3Storage

class UserS3Storage(S3Boto3Storage):
    def get_location(self, name):
        if name.startswith("users/"):
            return "users"
        
    def _normalize_name(self, name):
        if name.startswith("users/"):
            return name
        return f"users/{name}"