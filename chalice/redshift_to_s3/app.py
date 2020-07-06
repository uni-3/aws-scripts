import pandas as pd
import psycopg2
import boto3
from func_timeout import func_timeout, FunctionTimedOut

import os
from io import StringIO

ClusterEndpoint = os.getenv('CLUSTER_ENDPOINT', '')
ClusterIdentifier = os.getenv('CLUSTER_IDENTIFIER', '')
DBPort = os.getenv('DB_PORT', 5439)
DBName = os.getenv('DB_NAME', '')
DBUser = os.getenv('DB_USER', '')
QueryPath = os.getenv('QUERY_PATH', 'sql/test.sql')
S3Bucket = os.getenv('S3_BUCKET', 'bucket')
S3Path = os.getenv('S3_PATH', 'upload/path')
OutputFileName = os.getenv('OUTPUT_FILENAME', 'test')

from chalice import Chalice

app = Chalice(app_name='redshift_to_s3')


def load_query() -> str:
    """

    Returns
    -------
    query : string
        query string
    """

    filename = os.path.join(
        os.path.dirname(__file__), 'chalicelib', QueryPath)

    with open(filename) as f:
        query = f.read()

    return query


def get_param() -> dict:
    """
    Parameters
    ----------

    Returns
    ----------
    param : dict
        conn info
    """
    redshift = boto3.client('redshift')
    credentials = redshift.get_cluster_credentials(
        DbUser=DBUser,
        DbName=DBName,
        ClusterIdentifier=ClusterIdentifier,
        DurationSeconds=3600,
        AutoCreate=False
    )
    tmp_db_user = credentials['DbUser']
    tmp_db_password = credentials['DbPassword']

    param = {
        'host': ClusterEndpoint,
        'port': DBPort,
        'dbname': DBName,
        'user': tmp_db_user,
        'password': tmp_db_password
    }

    return param


def exec_query(query: str, timeout=3600):
    """
    exec query then, return df

    Parameters
    ----------
    query : string
        query string
    timeout : int
        limit for timeout

    Returns
    ----------
    result : pd.DataFrame
    """

    with psycopg2.connect(**get_param()) as conn:
        try:
            result = func_timeout(int(timeout), pd.read_sql, args=(query, conn))
            print('read sql')

        except FunctionTimedOut:
            result = None

        except Exception as e:
            print(e)
            result = None

    conn.close()
    print('conn object status is :', conn)

    return result


def dataframe_to_s3(df: pd.DataFrame, filename: str, output_s3_path: str) -> None:
    """
    Write a dataframe to a CSV on S3

    Parameters
    ----------
    df : pd.DataFrame
    filename : str
    output_s3_path : str

    Returns
    -------

    """
    print(f"Writing {len(df)} records to {S3Bucket + '/' + output_s3_path + filename + '.csv'}")
    # Create buffer
    csv_buffer = StringIO()
    # Write dataframe to buffer
    df.to_csv(csv_buffer, sep=",", index=False)

    s3_client = boto3.client('s3')
    s3_client.put_object(
        Bucket=S3Bucket,
        Key=output_s3_path+filename+'.csv',
        Body=csv_buffer.getvalue()
    )

    print(f'put s3://{S3Bucket}/{output_s3_path+filename}.csv')


@app.lambda_function(name='redshift_to_s3')
def main(event, context) -> None:
    query = load_query()
    res = exec_query(query)
    dataframe_to_s3(res, filename=OutputFileName, output_s3_path=S3Path)


