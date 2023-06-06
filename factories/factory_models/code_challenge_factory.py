import factory
from factory.alchemy import SQLAlchemyModelFactory

import factories.factory_session as sess
import src.data_access.postgresql.tables.code_challenge as resource


class CodeChallengeMethodFactory(SQLAlchemyModelFactory):
    class Meta:
        model = resource.CodeChallengeMethod
        sqlalchemy_session = sess.session

    method = factory.Faker("word")
