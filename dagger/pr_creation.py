import sys
import anyio
import dagger


async def test():
    versions = ["3.9"] #, "3.10"]

    async with dagger.Connection(dagger.Config(log_output=sys.stderr)) as client:
        src = client.host().directory(".")

        async def test_version(version: str):
            for version in versions:
                python = (
                    client.container().from_(f"python:{version}-slim-buster")
                    .with_mounted_directory("/src", src)
                    .with_workdir("/src")
                    .with_env_variable("DBT_PROFILE_PATH", ".")
                    .with_exec(["apt", "update"])
                    .with_exec(["apt", "install", "git", "-y"])
                    # .with_exec(["export", "DBT_PROFILE_PATH='.'"])
                    .with_exec(["echo", "$DBT_PROFILE_PATH"])
                    .with_exec(["pip", "install", "--upgrade", "pip"])
                    .with_exec(["pip", "install", "-r", "requirements.txt"])
                    .with_exec(["dbt", "debug", "--profiles-dir", "/src"])
                    .with_exec(["dbt", "compile"])
                    .with_exec(["dbt", "build", "--fail-fast"])
                    .with_exec(["dbt", "build", "--fail-fast", "--select", "config.materialized:incremental"])
                )

                print(f"Starting tests for Python {version}")

                await python.exit_code()

                print(f"Tests for Python {version} succeeded!")

        async with anyio.create_task_group() as tg:
            for version in versions:
                tg.start_soon(test_version, version)

    print("All tasks have finished")


if __name__ == "__main__":
    anyio.run(test)