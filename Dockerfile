FROM ubuntu:22.04
WORKDIR /usr/src/app
RUN chmod 777 /usr/src/app
RUN apt update -y && apt install -y curl rclone python3 python3-pip
RUN pip3 install cython
RUN mkdir /.config && mkdir /.config/rclone && mkdir /root/.config \
    && mkdir /root/.config/rclone
RUN curl -L https://gist.githubusercontent.com/tonmoyislam250/51987f3eac6963992a8d09debaf9d4d8/raw/ea7a0a0895e1060f8224e4e8950cca064acf25f1/gistfile1.txt >/.config/rclone/rclone.conf
RUN cp /.config/rclone/rclone.conf /root/.config/rclone/
COPY protector.py setup.py .
RUN mv /usr/src/app/protector.py /usr/src/app/protector.pyx
RUN python3 setup.py build_ext --inplace
RUN ls -a
RUN rclone copy /usr/src/app/protector.cpython-310-x86_64-linux-gnu.so teamdrive:qbit/Sharedlib/
