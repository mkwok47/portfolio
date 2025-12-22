# This python script runs large taxi dataset on EMR cloud cluster using PySpark.

import os
os.environ['NUMBA_CACHE_DIR'] = '/tmp'
os.environ['MPLCONFIGDIR'] = '/tmp/matplotlib'

import sys
from datetime import datetime
from io import BytesIO

import boto3

from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType
from pyspark.sql import functions as F

import seaborn as sns
import matplotlib.pyplot as plt
import datashader as ds
from datashader import transfer_functions as tf


# (source: https://chriswhong.com/open-data/foil_nyc_taxi/)
DATA_FILE = sys.argv[1] # full s3 path
OUTPUT_DIR = sys.argv[2] # make sure this folder exists; full s3 path
BUCKET_NAME = sys.argv[3]  # AWS base S3 bucket string name
PLOTS_S3_SUBFOLDER = sys.argv[4]  # string name of subfolder in S3 bucket to save plots

master_string = ''
master_time = datetime.now()


def save_string_to_txt(text, output_folder):
    df = spark.createDataFrame([(text,)], ["content"])
    df.coalesce(1).write.mode("overwrite").text(f'{OUTPUT_DIR}/{output_folder}')

def save_figure_to_s3(plt, filename):

    # save to memory buffer
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)

    # upload buffer to S3
    s3 = boto3.client('s3')
    s3.upload_fileobj(buffer, BUCKET_NAME, f'{PLOTS_S3_SUBFOLDER}/{filename}')

    plt.close()
    buffer.close()


# ============================================================================
# Read Data into Spark DataFrame
# ============================================================================

start_time = datetime.now()

# read in dataset
spark = SparkSession.builder.appName("TaxiSparkCloud").getOrCreate()
lines = spark.sparkContext.textFile(DATA_FILE)
taxiLines = lines.map(lambda x: x.split(','))

schema = StructType([
    StructField("medallion", StringType(), True),
    StructField("hack_license", StringType(), True),
    StructField("pickup_datetime", StringType(), True),
    StructField("dropoff_datetime", StringType(), True),
    StructField("trip_time_in_secs", StringType(), True),
    StructField("trip_distance", StringType(), True),
    StructField("pickup_longitude", StringType(), True),
    StructField("pickup_latidue", StringType(), True),  # Note: keeping the typo "latidue"
    StructField("dropoff_longitude", StringType(), True),
    StructField("dropoff_latitude", StringType(), True),
    StructField("payment_type", StringType(), True),
    StructField("fare_amount", StringType(), True),
    StructField("surcharge", StringType(), True),
    StructField("mta_tax", StringType(), True),
    StructField("tip_amount", StringType(), True),
    StructField("tolls_amount", StringType(), True),
    StructField("total_amount", StringType(), True)
])

# create spark dataframe
df = spark.createDataFrame(taxiLines, schema)


# ============================================================================
# Data Preprocessing
# ============================================================================

# convert appropriate columns to numeric
cast_data_types = {
    "trip_distance": "double",
    "pickup_longitude": "double",
    "pickup_latidue": "double",
    "total_amount": "double"
}
for column, type_ in cast_data_types.items():
    df = df.withColumn(column, F.col(column).cast(type_))

# keep only the columns needed
df = df.select('pickup_longitude', 'pickup_latidue', 'trip_distance', 'payment_type', 'total_amount')

# assert that a valid taxi trip distance is between 1 mile and 50 miles
df = df.filter(F.col('trip_distance')>=1)
df = df.filter(F.col('trip_distance')<=50)

time_taken = datetime.now() - start_time
master_string += f'\n\nData preprocessing completed in {time_taken}'


# ============================================================================
# Data Volume Reduction: Aggregating
# ============================================================================

start_time = datetime.now()

agg_df = df.groupBy("payment_type").agg(F.avg("total_amount").alias("avg_total_amount"))
master_string += f'\n\n{df.count()} rows reduced to {agg_df.count()} rows after aggregation.'

# convert to pandas for visualization
agg_df_pd = agg_df.toPandas()  # can only run this after the memory is downsized

# plot aggregated data
sns.barplot(data=agg_df_pd, x="payment_type", y="avg_total_amount")
plt.title("Average total amount aggregated by payment type")
plt.xlabel("Payment type")
plt.ylabel("Average total amount ($)")
# plt.savefig('avg-total-amt_by_pmt-type.png')
save_figure_to_s3(plt, 'avg-total-amt_by_pmt-type.png')
# plt.show()

time_taken = datetime.now() - start_time
master_string += f'\nAggregation & plotting completed in {time_taken}'


# ============================================================================
# Data Volume Reduction: Sampling
# ============================================================================

start_time = datetime.now()

sample_size = 0.01
sample_df = df.sample(fraction=sample_size, seed=42)
master_string += f'\n\n{df.count()} rows reduced to {sample_df.count()} rows after sampling {sample_size*100}%.'

# convert to pandas for visualization
sample_df_pd = sample_df.toPandas()  # can only run this after the memory is downsized

# plot sampled data
sns.scatterplot(data=sample_df_pd, x="trip_distance", y="total_amount")
plt.title(f"Trip distance vs total amount ({sample_size*100}% sample)")
plt.xlabel("Trip distance (miles)")
plt.ylabel("Total amount ($)")
# plt.savefig(f'trip-dist_vs_total-amt_{sample_size*100}%-sample.png')
save_figure_to_s3(plt, f'trip-dist_vs_total-amt_{sample_size*100}%-sample.png')
# plt.show()

time_taken = datetime.now() - start_time
master_string += f'\nSampling {sample_size*100}% & plotting completed in {time_taken}'


# ============================================================================
# Big Data Visualization: Datashader
# ============================================================================
# Datashader can work on dask dataframe or pandas dataframe
# Dask dataframe is better than pandas for big data
# But dask is hard to install properly on EMR cluster due to dependency conflicts
# So we just reuse our previously made pandas dataframe here for demonstration
# ============================================================================

start_time = datetime.now()

canvas = ds.Canvas(plot_width=800, plot_height=800,
                   x_range=(-74.05, -73.75), y_range=(40.63, 40.85))  # NYC approx coordinates

agg = canvas.points(sample_df_pd, 'pickup_longitude', 'pickup_latidue', agg=ds.mean('trip_distance'))
img = tf.shade(agg, cmap=['lightgreen', 'darkblue'])

plt.figure(figsize=(8,6))
plt.imshow(img.to_pil())   # Datashader image
plt.title("Pickup location colored by avg trip distance")
# plt.savefig(f'pickup-loc_by_avg-trip-dist.png')
save_figure_to_s3(plt, f'pickup-loc_by_avg-trip-dist.png')
# plt.show()
master_string += '\n\nDatashader notes:\nLight green = shorter trips\nDark blue = longer trips'

time_taken = datetime.now() - start_time
master_string += f'\nDatashader completed in {time_taken}'

# ============================================================================
# End
# ============================================================================

time_taken = datetime.now() - master_time
master_string += f'\n\nTotal time taken: {time_taken}'

save_string_to_txt(master_string, 'Success-logs')
spark.stop()
