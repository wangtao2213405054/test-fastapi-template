# _author: Coke
# _date: 2024/9/14 上午10:05
# _description:

from sqlmodel import Session, create_engine

from src.initdb.manage import manage

sqlite_file_name = "root:123456@127.0.0.1:33306/client"
sqlite_url = f"mysql+mysqlconnector://{sqlite_file_name}"

engine = create_engine(sqlite_url, echo=True)


if __name__ == "__main__":
    with Session(engine) as session:
        manage(session)
