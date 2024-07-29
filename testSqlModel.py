
from sqlmodel import SQLModel, create_engine, Session, select
from src.api.auth.models.models import (
    UserTable, UserCreate,
    MenuTable, MenuCreate,
    RoleTable, RoleCreate,
    AffiliationTable
)
from src.api.auth.security import hash_password


sqlite_file_name = "root:123456@127.0.0.1:33306/client"
sqlite_url = f"mysql+mysqlconnector://{sqlite_file_name}"

engine = create_engine(sqlite_url, echo=True)


def create_db_and_tables():
    SQLModel.metadata.drop_all(engine)
    # SQLModel.metadata.create_all(engine)


def main():
    create_db_and_tables()

    # with Session(engine) as session:
    #     menu = MenuCreate(
    #         name="测试菜单",
    #         identifier="test"
    #     )
    #     db_menu = MenuTable.model_validate(menu)
    #     session.add(db_menu)
    #     session.commit()
    #
    #     role = RoleCreate(
    #         name="管理员",
    #         identifier="admin",
    #         identifier_list=["role"]
    #     )
    #     db_role = RoleTable.model_validate(role)
    #     session.add(db_role)
    #     session.commit()
    #     session.refresh(db_role)
    #
    #     affiliation = AffiliationTable(
    #         name="字节跳动"
    #     )
    #     db_affiliation = AffiliationTable.model_validate(affiliation)
    #     session.add(db_affiliation)
    #     session.commit()
    #     session.refresh(db_affiliation)
    #
    #     user = UserCreate(
    #         name="admin",
    #         username="admin",
    #         email="admin",
    #         mobile="18888888888",
    #         password=hash_password("123456"),
    #         roleId=db_role.id,
    #         affiliationId=db_affiliation.id
    #     )
    #
    #     db_user = UserTable.model_validate(user)
    #     session.add(db_user)
    #     session.commit()
    #
    #     statement = select(RoleTable)
    #     results = session.exec(statement).one()
    #     print(results.users, 'tests')


if __name__ == "__main__":
    main()
