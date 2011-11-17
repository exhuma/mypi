from sqlalchemy import *
from migrate import *

metadata = MetaData()

packages_table = Table(
    'package', metadata,
    Column('name', String, primary_key=True),
    Column('inserted', DateTime, nullable=False, default=func.now()),
    Column('updated', DateTime, nullable=False, default=func.now()),

    #doc="A python package",
    )

users_table = Table(
    'user', metadata,
    Column('email', String, primary_key=True,
        doc="An email uniquely identifies a user account"),
    Column('full_name', String,
        doc="The user name"),
    Column('password', String,
        doc="A password hash"),
    Column('verified', Boolean, default=False,
        doc="Whether the user has verified his/her e-mail"),
    Column('verification_token', String,
        doc="A token used to verify the user's e-mail"),
    Column('verification_token_exires', DateTime,
        doc="The verification token expires after this date"),
    Column('inserted', DateTime, nullable=False, default=func.now(),
        doc="The timestamp when this user was registered in the system"),
    Column('updated', DateTime, nullable=False, default=func.now(),
        doc="The timestamp when the user was last modified"),
    #doc="A user in the system",
    )

package_auth = Table(
    'package_auth', metadata,
    Column('user', String, ForeignKey('user.email')),
    Column('package', String, ForeignKey('package.name')),
    Column('grant_mask', Integer,
        doc="Bitmask defining the rights granted to this user for this project"),
    PrimaryKeyConstraint('user', 'package'),
    #doc="Defines access rights to packages for users"
    )

release_table = Table(
    'release', metadata,
    Column('package', String, ForeignKey('package.name'),
        doc="The reference to the package"),
    Column('license', String,
        doc="The license name"),
    Column('metadata_version', String,
        doc="The metadata version (from setup.py)"),
    Column('author_email', String, ForeignKey('user.email'),
        doc="The author email (=the user uploading the package)"),
    Column('home_page', String,
        doc="The home page for this release"),
    Column('download_url', String,
        doc="A URL where the release can be downloaded"),
    Column('summary', String,
        doc="Summary description"),
    Column('version', String,
        doc="Release version string"),
    Column('platform', String,
        doc="Target platform for this release"),
    Column('description', String,
        doc="Long description"),
    Column('inserted', DateTime, nullable=False, default=func.now(),
        doc="Timestamp when the release was added/uploaded"),
    Column('updated', DateTime, nullable=False, default=func.now(),
        doc="Timestamp when this release was last edited"),
    PrimaryKeyConstraint('package', 'version'),
    #doc="Metadata for one package release"
    )

files_table = Table(
    'file', metadata,
    Column('package', String,
        doc="The package to which this file belongs to"),
    Column('author_email', String,
        ForeignKey('user.email'),
        doc="The user who uploaded this file"),
    Column('version', String,
        doc="The package version for this file"),
    Column('md5_digest', String(32),
        doc="MD5 Hash of the file contents"),
    Column('filename', Unicode,
        doc="The filename"),
    Column('comment', String,
        doc="Comment as specified by the uploader"),
    Column('filetype', String,
        doc="File type"),
    Column('pyversion', String,
        doc="Target python version"),
    Column('protcol_version', Integer),
    Column('data', LargeBinary),
    Column('inserted', DateTime, nullable=False, default=func.now(),
        doc="Timestamp when this file was uploaded"),
    Column('updated', DateTime, nullable=False, default=func.now(),
        doc="Timestamp when this file was last edited"),

    PrimaryKeyConstraint('package', 'version', 'filetype'),
    UniqueConstraint('package', 'filename'),
    ForeignKeyConstraint(('package', 'version'),
                         ('release.package', 'release.version')),
    )


def upgrade(migrate_engine):
    metadata.bind = migrate_engine
    users_table.create()
    packages_table.create()
    package_auth.create()
    release_table.create()
    files_table.create()


def downgrade(migrate_engine):
    metadata.bind = migrate_engine
    files_table.drop()
    release_table.drop()
    packages_table.drop()
    users_table.drop()
    package_auth.drop()
