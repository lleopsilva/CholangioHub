from services.processing.app.jobs.process_silver import build_spark_session


def test_build_spark_session_sets_hadoop_s3a_timeouts(monkeypatch):
    captured = {}

    class DummySparkSession:
        class sparkContext:
            _jsc = type(
                "Jsc",
                (),
                {
                    "hadoopConfiguration": lambda self: type(
                        "Conf",
                        (),
                        {"set": lambda self, key, value: captured.setdefault(key, value)},
                    )()
                },
            )()

    class DummyBuilder:
        def appName(self, _):
            return self

        def master(self, _):
            return self

        def config(self, key, value):
            captured[key] = value
            return self

        def getOrCreate(self):
            return DummySparkSession()

    class DummySparkSessionModule:
        class builder:
            @staticmethod
            def appName(_):
                return DummyBuilder()

        class SparkSession:
            @staticmethod
            def builder():
                return DummyBuilder()

    monkeypatch.setattr(
        "services.processing.app.jobs.process_silver.SparkSession",
        DummySparkSessionModule,
    )

    build_spark_session()

    assert (
        captured["spark.jars.packages"]
        == "org.apache.hadoop:hadoop-aws:3.5.0,com.amazonaws:aws-java-sdk-bundle:1.12.720"
    )
    assert captured["spark.hadoop.fs.s3a.connection.timeout"] == "60000"
    assert captured["spark.hadoop.fs.s3a.socket.timeout"] == "60000"
