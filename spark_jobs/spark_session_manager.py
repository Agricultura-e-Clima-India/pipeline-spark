from pyspark.sql import SparkSession


def get_spark_session(app_name: str = "Data Pipeline") -> SparkSession:
    """Create or return a SparkSession configured for local development."""
    builder = (
        SparkSession.builder.appName(app_name)
        .config("spark.sql.session.timeZone", "UTC")
        .config("spark.sql.shuffle.partitions", "4")
        .config("spark.sql.parquet.mergeSchema", "true")
        .config("spark.sql.execution.arrow.pyspark.enabled", "true")
    )
    return builder.getOrCreate()
