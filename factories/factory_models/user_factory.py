import factory
from factory.alchemy import SQLAlchemyModelFactory
from factory.fuzzy import FuzzyChoice
from typing import Any
import factories.data.data_for_factories as data
import factories.factory_session as sess
import src.data_access.postgresql.tables.users as users
from src.data_access.postgresql.tables import Role, User

class UserPasswordFactory(SQLAlchemyModelFactory):
    class Meta:
        model = users.UserPassword
        sqlalchemy_session = sess.session
        
    value = factory.Iterator(data.CLIENT_HASH_PASSWORDS.values())


class UserFactory(SQLAlchemyModelFactory):
    class Meta:
        model = users.User
        sqlalchemy_session = sess.session
        sqlalchemy_get_or_create = ("username",)

    email = factory.Faker("ascii_email")
    email_confirmed = factory.Faker("pybool")
    password_hash_id = factory.SubFactory(UserPasswordFactory)
    security_stamp = factory.Faker("word")
    phone_number = factory.Faker("phone_number")
    phone_number_confirmed = factory.Faker("pybool")
    two_factors_enabled = factory.Faker("pybool")
    lockout_end_date_utc = factory.Faker("date_time")
    lockout_enabled = factory.Faker("pybool")
    access_failed_count = factory.Faker("random_int")
    username = factory.Iterator(data.CLIENT_USERNAMES.values())

    @factory.post_generation
    def roles(self, create:Any, extracted:list[Role], **kwargs:Any) -> None:
        if not create:
            # Simple build, do nothing.
            return
        if extracted:
            # A list of roles were passed in, use them
            for role in extracted:
                self.roles.append(role)



class UserLoginFactory(SQLAlchemyModelFactory):
    class Meta:
        model = users.UserLogin
        sqlalchemy_session = sess.session
        sqlalchemy_get_or_create = ("login_provider",)

    user_id = factory.SubFactory(UserFactory)
    login_provider = factory.Faker("word")
    provider_key = factory.Faker("word")


class RoleFactory(SQLAlchemyModelFactory):
    class Meta:
        model = users.Role
        sqlalchemy_session = sess.session

    name = factory.Faker("job")

    @factory.post_generation
    def users(self, create: Any, extracted:list[User], **kwargs:Any) -> Any:
        if not create:
            # Simple build, do nothing.
            return
        if extracted:
            # A list of users were passed in, use them
            for user in extracted:
                self.users.append(user)


class UserClaimTypeFactory(SQLAlchemyModelFactory):
    class Meta:
        model = users.UserClaimType
        sqlalchemy_session = sess.session

    type_of_claim = FuzzyChoice(data.USER_CLAIM_TYPE)


class UserClaimFactory(SQLAlchemyModelFactory):
    class Meta:
        model = users.UserClaim
        sqlalchemy_session = sess.session

    user_id = factory.SubFactory(UserFactory)
    claim_type_id = factory.SubFactory(UserClaimTypeFactory)
    claim_value = factory.Faker("word")


class UserRolesFactory(SQLAlchemyModelFactory):
    class Meta:
        model = users.users_roles
        sqlalchemy_session = sess.session

    role = factory.SubFactory(RoleFactory)
    user = factory.SubFactory(UserFactory)
