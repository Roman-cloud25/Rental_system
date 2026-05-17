"""
File storage settings for AWS S3.
"""

from storages.backends.s3boto3 import S3Boto3Storage

# Images storage
class MediaStorage(S3Boto3Storage):
    location = 'media'
    # Do not overwrite files with the same name
    file_overwrite = False