from services.processing.app.jobs.process_silver import build_spark_session

spark = build_spark_session(app_name='debug')
conf = spark.sparkContext._jsc.hadoopConfiguration()
keys = [
    'fs.s3a.connection.timeout',
    'fs.s3a.socket.timeout',
    'fs.s3a.endpoint',
    'fs.s3a.path.style.access',
    'fs.s3a.impl',
]
for key in keys:
    print(key, '=>', conf.get(key))
spark.stop()
