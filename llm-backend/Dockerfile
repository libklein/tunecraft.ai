FROM public.ecr.aws/lambda/python:3.12

# Install blas
RUN dnf install -y blas-devel blas blas64 clang

# Install llama-cpp
RUN CMAKE_ARGS="-DLLAMA_BLAS=ON -DLLAMA_BLAS_VENDOR=OpenBLAS" pip install llama-cpp-python

COPY libklein ${LAMBDA_TASK_ROOT}/libklein
COPY instance ${LAMBDA_TASK_ROOT}/instance
COPY app.py requirements.txt ${LAMBDA_TASK_ROOT}/
COPY instance/config.py ${LAMBDA_TASK_ROOT}/

# Install flask and other dependencies
RUN pip install -r requirements.txt


CMD [ "app.handler" ]
