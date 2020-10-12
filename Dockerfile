FROM xuhshen/basepython:latest

ENV workspace /home
WORKDIR ${workspace}
COPY ./ ./develop/ 
COPY requirement.txt ./ 

RUN pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple \
    && pip uninstall -y numpy \
    && pip install tensorflow==2.3.1 --ignore-installed six  -i https://pypi.tuna.tsinghua.edu.cn/simple \
    && pip install -r requirement.txt -i https://pypi.tuna.tsinghua.edu.cn/simple \
	&& rm -fr ~/.cache/pip

ENV PYTHONPATH="${workspace}/develop:$PYTHONPATH"

CMD ["python","/home/develop/run/main.py"]