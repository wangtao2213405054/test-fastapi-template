
from sqlmodel import SQLModel, create_engine, Session, select
from src.auth.models import UserTable, UserCreate, MenuTable, MenuCreate, RoleTable, RoleCreate, UserRead


sqlite_file_name = "root:123456789@127.0.0.1:3306/client"
sqlite_url = f"mysql+mysqlconnector://{sqlite_file_name}"

engine = create_engine(sqlite_url, echo=True)


def create_db_and_tables():
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)


def main():
    create_db_and_tables()

    with Session(engine) as session:
        menu = MenuCreate(
            name="测试菜单",
            identifier="test"
        )
        db_menu = MenuTable.model_validate(menu)
        session.add(db_menu)
        session.commit()

        role = RoleCreate(
            name="管理员",
            identifier="admin"
        )
        db_role = RoleTable.model_validate(role)
        session.add(db_role)
        session.commit()
        session.refresh(db_role)

        user = UserCreate(
            name="王涛",
            email="2213405054@qq.com",
            mobile="13520421043",
            password="1123",
            nodeId=1,
            roleId=db_role.id
        )

        db_user = UserTable.model_validate(user)
        session.add(db_user)
        session.commit()

        statement = select(RoleTable)
        results = session.exec(statement).one()
        print(results.users, 'test')


if __name__ == "__main__":
    main()
