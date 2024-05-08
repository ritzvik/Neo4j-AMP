import subprocess
from utils.check_dependency import check_gpu_enabled

print(subprocess.run(["sh 0_session-install-dependencies/setup.sh"], shell=True))

if check_gpu_enabled():
    print(
        subprocess.run(["sh 0_session-install-dependencies/setup_gpu.sh"], shell=True)
    )
else:
    print(
        subprocess.run(
            ["sh 0_session-install-dependencies/setup_cpu_only.sh"], shell=True
        )
    )
