from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, select, MetaData

Base = automap_base()
engine = create_engine("mysql://pi:aptx4869@147.182.137.230:3306/flight_data")
Base.prepare(autoload_with=engine)
metadata = MetaData()
metadata.reflect(bind=engine)
session = Session(engine)

# mapped classes are now created with names by default
# matching that of the table name.
Airport = Base.classes.airport
#TempUnitedAward = MetaData.tables["temp_united_award"]


if __name__ == "__main__":
    print(Airport)
    stmt = select(Airport).where(Airport.iata == "PHL")

    result = session.scalars(stmt)
    print(result.one())

    print(session.scalar(select(Airport).where(Airport.iata == "LAX")).country)
