from logging.config import fileConfig
import sre_compile

from sqlalchemy import engine_from_config
from sqlalchemy import pool
import app.core.models as models

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
import app.core.models as models
target_metadata = models.BaseModel.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

# load database URI from cmdline param
database_uri = context.get_x_argument(as_dictionary=True).get('database_uri', None)
if database_uri is not None:
    config.set_main_option('sqlalchemy.url', database_uri)

def render_item(type_, obj, autogen_context):
    """Custom renderer for IntEnumField columns with params"""
    if type_ == 'type' and isinstance(obj, models.IntEnumField):
        autogen_context.imports.add(f'import {obj.__class__.__module__}')
        if hasattr(obj, '_enum_type'):
            autogen_context.imports.add(f'import {obj._enum_type.__module__}')
            return f'{obj.__class__.__module__}.{obj.__class__.__name__}(enum_type={obj._enum_type.__module__}.{obj._enum_type.__name__})'

    return False

def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        user_module_prefix='app.core.models',
        render_item=render_item
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata, render_item=render_item
        )

        with context.begin_transaction():
            context.run_migrations()



if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
