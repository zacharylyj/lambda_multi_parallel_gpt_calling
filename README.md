# Sentiment Analysis Lambda Function

This Lambda function performs sentiment analysis on text data using asynchronous calls to an API. It is designed to process and analyze batches of sentences, extracting sentiment scores, themes, and keywords.

## Functionality

- **Sentiment Analysis**: Provides a sentiment score between 0 (negative) and 10 (positive).
- **Theme Classification**: Classifies the text into predefined categories and extracts keywords.
- **Batch Processing**: Supports processing of large sets of sentences in chunks.

## Environment Variables

- `API_KEY`: Required for API authentication.

## Dependencies

- `numpy`: Used for data manipulation.
- `aiohttp`: Asynchronous HTTP client for making API requests.
- `asyncio`: For asynchronous programming.
- `json`: For JSON parsing.
- `ast`: For safely evaluating strings containing Python literals.

## Usage

1. **Deploy**: Deploy this function to AWS Lambda.
2. **Invoke**: Trigger the function with an event containing the text data.
3. **Process**: The function processes the input in batches and calls the API asynchronously.
4. **Output**: Returns a list of analyzed data including scores, themes, and keywords.

## API Integration

- The function dynamically constructs API endpoint URLs for load balancing across multiple API instances.
- Uses POST requests to send data to the API and handles responses asynchronously.

## Rate Limiting

- Handles API rate limits by delaying the next request based on the `Retry-After` header.

## Debugging

- Debugging can be enabled by setting the `DEBUG` variable. This will print additional output for troubleshooting.

## Example Payload

```json
{
  "body": "{\"data\": [\"sentence 1\", \"sentence 2\"]}"
}
```

## Security

- API keys are obscured in logs to prevent exposure.

## Limitations
- Ensure the environment variable API_KEY is set correctly.
- Adjust ```CHUNK_SIZE``` and ```DELAY_BETWEEN_CHUNKS``` as needed based on the API's capacity and rate limits.
