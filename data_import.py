import pandas_geojson as pdg
from typing import List
from sqlalchemy import create_engine, String, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, Mapped, mapped_column, relationship

# format data for pandas
library_geojson = pdg.read_geojson('data/tpl-branch-general-information - 4326.geojson')
library_df = library_geojson.to_dataframe()

# relevant columns
library_columns = [
    'properties.BranchName', 
    'properties.Address', 
    'properties.Website', 
    'properties.SquareFootage', 
    'properties.PublicParking',
    'properties.PublicWashroom',
    'properties.Hours',
    ]

relevant_library_df = library_df[library_columns]

engine = create_engine('sqlite:///database.db', echo=True)

Base = declarative_base()

class Amenity(Base):
    __tablename__ = 'amenity'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(), nullable=False)
    type_id: Mapped[int] = mapped_column(ForeignKey("amenity_type.id"))
    address: Mapped[str] = mapped_column(String())

    amenity_type: Mapped["AmenityType"] = relationship(back_populates="amenities")

class AmenityType(Base):
    __tablename__ = 'amenity_type'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] =  mapped_column(String(), nullable=False)

    amenities: Mapped[List["Amenity"]] = relationship(back_populates="amenity_type")

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)

if __name__ == "__main__":
    pass

    # with Session() as session:
    #     new_amenities_type = AmenityType(name='Library')
    #     session.add(new_amenities_type)
    #     session.commit()

    # with Session() as session:
    #     for l in relevant_library_df.iterrows():
    #         # check if entry is already in the database
    #         try:
    #             present_result = session.query(Amenity).filter(Amenity.name == l[1]['properties.BranchName']).one()
    #             # TODO instead of .one() and getting an exception there might be something sqlalchemy has
    #             print(f"{l[1]['properties.BranchName']} already has already been added")
    #         except:
    #             print(f"{l[1]['properties.BranchName']} has NOT been added yet, adding now ...")
    #             new_libary = Amenity(
    #                 name=l[1]['properties.BranchName'],
    #                 type_id=1, # 1 - Library ; TODO update this reference to be dynamic
    #                 address=l[1]['properties.Address'],
    #                 )
    #             session.add(new_libary)
    #     session.commit() # TODO should I commit for every entry or after reading the entire db?

