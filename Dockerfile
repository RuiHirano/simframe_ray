FROM rayproject/ray

COPY . .
RUN pip3 install --upgrade pip
RUN pip3 install -e .

CMD [ "bash"]