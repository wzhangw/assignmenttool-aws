import datetime
AWS_ACCESS_KEY_ID = "AKIASA4PVV5EJ6OEGXK2"
AWS_SECRET_ACCESS_KEY = "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"
AWS_FILE_EXPIRE = 200
AWS_PRELOAD_METADATA = True
AWS_QUERYSTRING_AUTH = True

#DEFAULT_FILE_STORAGE = 'sa3.aws.utils.MediaRootS3BotoStorage'
STATICFILES_STORAGE = 'sa3.aws.utils.StaticRootS3BotoStorage'
AWS_STORAGE_BUCKET_NAME = 'django-static-saaa'
S3DIRECT_REGION = 'us-east-2'
S3_URL = 'https://django-static-saaa.s3.amazonaws.com/' #% AWS_STORAGE_BUCKET_NAME
#MEDIA_URL = 'https://django-static-saaa.s3.amazonaws.com/media/' #% AWS_STORAGE_BUCKET_NAME
#MEDIA_ROOT = MEDIA_URL
STATIC_URL = S3_URL + 'static/'
ADMIN_MEDIA_PREFIX = STATIC_URL + 'admin/'

AWS_S3_REGION_NAME = 'us-east-2'
AWS_S3_SIGNATURE_VERSION = 's3v4'

two_months = datetime.timedelta(days=61)
date_two_months_later = datetime.date.today() + two_months
expires = date_two_months_later.strftime("%A, %d %B %Y 20:00:00 GMT")

AWS_HEADERS = {
    'Expires': expires,
    'Cache-Control': 'max-age=%d' % (int(two_months.total_seconds()), ),
}
