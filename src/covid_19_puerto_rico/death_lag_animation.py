# This is in a separate file because it's kinda hardcoded and I don't want to
# run it all the time.  It generates frames for an animated GIF.
from sqlalchemy.sql import text
import altair as alt
import logging
import pandas as pd
from .util import *


def death_lag_animation(connection, args):
    for current_date in pd.date_range(args.earliest_bulletin_date, args.bulletin_date):
        df = death_lag_animation_data(connection,
                                      args.earliest_bulletin_date,
                                      current_date)
        logging.info("death_lag_animation frame: %s", describe_frame(df))

        basename = f"{args.output_dir}/death_lag_animation_{current_date}"
        save_chart(death_lag_animation_chart(df, args), basename, args.output_formats)

def death_lag_animation_chart(df, args):
    return alt.Chart(df).mark_line(point=True).encode(
        x=alt.X('datum_date', title='Fecha',
                scale=alt.Scale(domain=(pd.to_datetime(args.earliest_bulletin_date),
                                        pd.to_datetime(args.bulletin_date)))),
        y=alt.Y('value', title=None, scale=alt.Scale(domain=(80, 100))),
        color=alt.Color('variable', title=None,
                        legend=alt.Legend(orient="top", labelLimit=250)),
    ).properties(
        width=600
    )

def death_lag_animation_data(connection, earliest_bulletin_date, bulletin_date):
    query = text('''
        SELECT 
--            bulletin_date,
            datum_date,
            COALESCE(deaths, 
                    MAX(deaths) OVER (PARTITION BY bulletin_date ROWS UNBOUNDED PRECEDING)) deaths,
            announced_deaths
        FROM products.cumulative_data
        WHERE :earliest_bulletin_date <= datum_date 
        AND datum_date <= bulletin_date
        AND bulletin_date = :bulletin_date
        ORDER BY bulletin_date, datum_date''')\
        .bindparams(earliest_bulletin_date=earliest_bulletin_date,
                    bulletin_date=bulletin_date)
    df = pd.read_sql_query(query, connection)
    df = df.rename(columns={
        'announced_deaths': 'Muertes anunciadas',
        'deaths': 'Muertes revisadas'
    })
    return fix_and_melt(df, "datum_date")