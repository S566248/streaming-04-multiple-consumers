"""
    This program sends a message to a queue on the RabbitMQ server.
    Make tasks harder/longer-running by adding dots at the end of the message.

    Author: Tyler Stanton
    Date: May 24, 2024

"""

# Add imports
import pika
import sys
import webbrowser
import csv

# Set up logger
from util_logger import setup_logger

logger, logname = setup_logger(__file__)


def offer_rabbitmq_admin_site():
    """Offer to open the RabbitMQ Admin website"""
    ans = input("Would you like to monitor RabbitMQ queues? y or n ")
    print()
    if ans.lower() == "y":
        webbrowser.open_new("http://localhost:15672/#/queues")
        logger.info("Opened RabbitMQ")
        

def send_message(host: str, queue_name: str, message: str):
    """
    Creates and sends a message to the queue each execution.
    This process runs and finishes.

    Parameters:
        host (str): the host name or IP address of the RabbitMQ server
        queue_name (str): the name of the queue
        message (str): the message to be sent to the queue
    """

    try:
        # create a blocking connection to the RabbitMQ server
        conn = pika.BlockingConnection(pika.ConnectionParameters(host))
        # use the connection to create a communication channel
        ch = conn.channel()
        # use the channel to declare a durable queue
        # a durable queue will survive a RabbitMQ server restart
        # and help ensure messages are processed in order
        # messages will not be deleted until the consumer acknowledges
        ch.queue_declare(queue=queue_name, durable=True)
        # use the channel to publish a message to the queue
        # every message passes through an exchange
        ch.basic_publish(exchange="", routing_key=queue_name, body=message)
        # print a message to the console for the user
        logger.info(f" [x] Sent {message}")
    except pika.exceptions.AMQPConnectionError as e:
        logger.error(f"Error: Connection to RabbitMQ server failed: {e}")
        sys.exit(1)
    finally:
        # close the connection to the server
        conn.close()

# Emit tasks from tasks.csv to RabbitMQ server
def emit_tasks(file_path: str, host: str, queue_name: str):
    with open(file_path, newline='') as csv_file:
        reader = csv.reader(csv_file)
        for row in reader: 
            message = " ".join(row)
            send_message(host, queue_name, message)



if __name__ == "__main__":
    # Offers to open RabbitMQ admin page
    offer_rabbitmq_admin_site()
    # Define file_name variables file_name, host, and queue_name 
    file_name = 'tasks.csv'
    host = "localhost"
    queue_name = "task_queue3"
    # Send the tasks to the queue
    emit_tasks(file_name, host, queue_name)