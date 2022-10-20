#!/usr/bin/env python
"""
Download from W&B the raw dataset and apply some basic data cleaning,
exporting the result to a new artifact
"""
import argparse
import logging
import wandb
import pandas as pd


logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")
logger = logging.getLogger()


def go(args):

    run = wandb.init(job_type="basic_cleaning")
    run.config.update(args)

    # Download input artifact. This will also log that this script is using this
    # particular version of the artifact
    logger.info("Getting input artifact %s", args.input_artifact)
    artifact_local_path = run.use_artifact(args.input_artifact).file()
    logger.info("Got input artifact %s", args.input_artifact)

    # Reading data into pandas dataframe
    airbnb_df = pd.read_csv(artifact_local_path)

    # Drop outliers
    logger.info("Dropping outliers")
    keep_idx = airbnb_df['price'].between(args.min_price, args.max_price)
    airbnb_df = airbnb_df[keep_idx].copy()

    # To datetime conversion
    logger.info("Converting string date to datetime object")
    airbnb_df['last_review'] = pd.to_datetime(airbnb_df['last_review'])

    # Save to disk
    logger.info("Saving dataframe to disk")
    airbnb_df.to_csv('clean_sample.csv', index=False)

    #Log artifact
    artifact = wandb.Artifact(
        args.output_artifact,
        args.output_type,
        args.output_description
    )

    artifact.add_file('clean_sample.csv')
    run.log_artifact()



if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="A very basic data cleaning")


    parser.add_argument(
        "--input_artifact", 
        type=str,
        help="Name of the W&B artifact that this step consumes, containing"+
        " the data after the EDA step",
        required=True
    )

    parser.add_argument(
        "--output_artifact", 
        type=str,
        help="Name of the clean data W&B artifact that this step produces",
        required=True
    )

    parser.add_argument(
        "--output_type", 
        type=str,
        help="Type of the output artifact, e.g. clean_data",
        required=True
    )

    parser.add_argument(
        "--output_description", 
        type=str,
        help="Description for the output artifact",
        required=True
    )

    parser.add_argument(
        "--min_price", 
        type=float,
        help="Minimum night price to consider, in USD",
        required=True
    )

    parser.add_argument(
        "--max_price",
        type=float,
        help="Maximum night price to consider, in USD",
        required=True
    )


    args = parser.parse_args()

    go(args)
