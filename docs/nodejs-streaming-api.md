# Node.js Streaming API Documentation

This document provides comprehensive guidance on how to consume the `/arbitrate/stream` endpoint using Node.js with Server-Sent Events (SSE).

## Overview

The `/arbitrate/stream` endpoint provides real-time streaming of arbitration results using Server-Sent Events (SSE). This allows clients to receive incremental updates as the AI arbiter processes policy arbitration requests.

## Endpoint Details

- **URL**: `POST /arbitrate/stream`
- **Content-Type**: `application/json`
- **Response Type**: `text/event-stream`
- **Method**: POST

## Request Format

### Request Body Schema

```json
{
  "policy": {
    "id": "uuid4-string",
    "creator_id": "uuid4-string", 
    "name": "string",
    "description": "string (optional)",
    "created_at": "ISO-8601-datetime"
  },
  "opposer_evidences": [
    {
      "id": "uuid4-string",
      "policy_id": "uuid4-string",
      "submitter_id": "uuid4-string",
      "content": "string",
      "created_at": "ISO-8601-datetime"
    }
  ],
  "defender_evidences": [
    {
      "id": "uuid4-string", 
      "policy_id": "uuid4-string",
      "submitter_id": "uuid4-string",
      "content": "string",
      "created_at": "ISO-8601-datetime"
    }
  ],
  "user_query": "string (optional)"
}
```

### Response Stream Format

The endpoint returns Server-Sent Events in the following format:

```
data: {"type": "arbitration", "decision_type": "approve_opposer", "decision": "...", "confidence": 0.85, ...}

data: {"type": "complete", "message": "done"}

data: {"type": "error", "message": "Error description"}
```

## Node.js Implementation Examples

### Method 1: Using EventSource (Recommended)

```javascript
// npm install eventsource
const EventSource = require('eventsource');
const fetch = require('node-fetch'); // or use built-in fetch in Node.js 18+

async function streamArbitration(requestData) {
  try {
    // First, make the POST request to initiate streaming
    const response = await fetch('http://localhost:8000/arbitrate/stream', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'text/event-stream',
        'Cache-Control': 'no-cache'
      },
      body: JSON.stringify(requestData)
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    // Create EventSource from the response
    const eventSource = new EventSource(response.url);

    eventSource.onmessage = function(event) {
      try {
        const data = JSON.parse(event.data);
        
        switch(data.type) {
          case 'arbitration':
            console.log('Arbitration Update:', data);
            // Handle arbitration decision update
            handleArbitrationUpdate(data);
            break;
            
          case 'complete':
            console.log('Arbitration Complete');
            eventSource.close();
            break;
            
          case 'error':
            console.error('Arbitration Error:', data.message);
            eventSource.close();
            break;
            
          default:
            console.log('Unknown event type:', data.type);
        }
      } catch (parseError) {
        console.error('Error parsing event data:', parseError);
      }
    };

    eventSource.onerror = function(error) {
      console.error('EventSource error:', error);
      eventSource.close();
    };

    return eventSource;
    
  } catch (error) {
    console.error('Error starting arbitration stream:', error);
    throw error;
  }
}

function handleArbitrationUpdate(data) {
  // Process the arbitration decision update
  console.log(`Decision Type: ${data.decision_type}`);
  console.log(`Confidence: ${data.confidence}`);
  console.log(`Decision: ${data.decision}`);
  if (data.reasoning) {
    console.log(`Reasoning: ${data.reasoning}`);
  }
}
```

### Method 2: Using Raw HTTP Response Stream

```javascript
const https = require('https');
const http = require('http');

function streamArbitrationRaw(requestData, baseUrl = 'http://localhost:8000') {
  return new Promise((resolve, reject) => {
    const url = new URL('/arbitrate/stream', baseUrl);
    const isHttps = url.protocol === 'https:';
    const client = isHttps ? https : http;
    
    const postData = JSON.stringify(requestData);
    
    const options = {
      hostname: url.hostname,
      port: url.port || (isHttps ? 443 : 80),
      path: url.pathname,
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Content-Length': Buffer.byteLength(postData)
      }
    };

    const req = client.request(options, (res) => {
      if (res.statusCode !== 200) {
        reject(new Error(`HTTP ${res.statusCode}: ${res.statusMessage}`));
        return;
      }

      res.setEncoding('utf8');
      
      let buffer = '';
      
      res.on('data', (chunk) => {
        buffer += chunk;
        
        // Process complete SSE messages
        const lines = buffer.split('\n');
        buffer = lines.pop(); // Keep incomplete line in buffer
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.substring(6));
              handleStreamEvent(data);
              
              if (data.type === 'complete' || data.type === 'error') {
                res.destroy();
                resolve();
                return;
              }
            } catch (parseError) {
              console.error('Error parsing SSE data:', parseError);
            }
          }
        }
      });

      res.on('end', () => {
        resolve();
      });

      res.on('error', (error) => {
        reject(error);
      });
    });

    req.on('error', (error) => {
      reject(error);
    });

    req.write(postData);
    req.end();
  });
}

function handleStreamEvent(data) {
  switch(data.type) {
    case 'arbitration':
      console.log('📊 Arbitration Update:');
      console.log(`  Decision Type: ${data.decision_type}`);
      console.log(`  Confidence: ${(data.confidence * 100).toFixed(1)}%`);
      console.log(`  Decision: ${data.decision}`);
      break;
      
    case 'complete':
      console.log('✅ Arbitration completed successfully');
      break;
      
    case 'error':
      console.error('❌ Arbitration error:', data.message);
      break;
  }
}
```

### Method 3: Using Async Iterators (Modern Approach)

```javascript
async function* streamArbitrationAsync(requestData) {
  const response = await fetch('http://localhost:8000/arbitrate/stream', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'text/event-stream'
    },
    body: JSON.stringify(requestData)
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';

  try {
    while (true) {
      const { done, value } = await reader.read();
      
      if (done) break;
      
      buffer += decoder.decode(value, { stream: true });
      
      // Process complete SSE messages
      const lines = buffer.split('\n');
      buffer = lines.pop(); // Keep incomplete line
      
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.substring(6));
            yield data;
            
            if (data.type === 'complete' || data.type === 'error') {
              return;
            }
          } catch (parseError) {
            console.error('Error parsing SSE data:', parseError);
          }
        }
      }
    }
  } finally {
    reader.releaseLock();
  }
}

// Usage example
async function consumeArbitrationStream(requestData) {
  try {
    for await (const event of streamArbitrationAsync(requestData)) {
      switch(event.type) {
        case 'arbitration':
          console.log('Arbitration update received:', event);
          break;
        case 'complete':
          console.log('Stream completed');
          break;
        case 'error':
          console.error('Stream error:', event.message);
          break;
      }
    }
  } catch (error) {
    console.error('Error consuming stream:', error);
  }
}
```

## Complete Working Example

```javascript
// arbitration-client.js
const { v4: uuidv4 } = require('uuid');

// Sample request data
const sampleRequestData = {
  policy: {
    id: uuidv4(),
    creator_id: uuidv4(),
    name: "Remote Work Policy",
    description: "Policy allowing employees to work remotely 3 days per week",
    created_at: new Date().toISOString()
  },
  opposer_evidences: [
    {
      id: uuidv4(),
      policy_id: "same-as-policy-id",
      submitter_id: uuidv4(),
      content: "Remote work reduces team collaboration and productivity based on recent studies",
      created_at: new Date().toISOString()
    }
  ],
  defender_evidences: [
    {
      id: uuidv4(),
      policy_id: "same-as-policy-id", 
      submitter_id: uuidv4(),
      content: "Remote work increases employee satisfaction and reduces overhead costs",
      created_at: new Date().toISOString()
    }
  ],
  user_query: "Please evaluate this remote work policy dispute"
};

// Run the arbitration
async function main() {
  console.log('🚀 Starting arbitration stream...');
  
  try {
    await consumeArbitrationStream(sampleRequestData);
  } catch (error) {
    console.error('Failed to process arbitration:', error);
  }
}

if (require.main === module) {
  main();
}
```

## Error Handling

### Common Error Scenarios

1. **Network Errors**: Connection timeouts, network interruptions
2. **HTTP Errors**: 4xx/5xx status codes from the server
3. **Parse Errors**: Invalid JSON in SSE data
4. **Stream Interruptions**: Unexpected connection closures

### Error Handling Best Practices

```javascript
function createRobustStreamClient(requestData, options = {}) {
  const {
    maxRetries = 3,
    retryDelay = 1000,
    timeout = 30000
  } = options;

  let retryCount = 0;

  async function attemptStream() {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), timeout);

      const response = await fetch('http://localhost:8000/arbitrate/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'text/event-stream'
        },
        body: JSON.stringify(requestData),
        signal: controller.signal
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return response;
      
    } catch (error) {
      if (retryCount < maxRetries && !error.name === 'AbortError') {
        retryCount++;
        console.log(`Retry attempt ${retryCount}/${maxRetries} after ${retryDelay}ms`);
        await new Promise(resolve => setTimeout(resolve, retryDelay));
        return attemptStream();
      }
      throw error;
    }
  }

  return attemptStream();
}
```

## Testing

### Unit Test Example (Jest)

```javascript
// arbitration-stream.test.js
const { streamArbitrationAsync } = require('./arbitration-client');

describe('Arbitration Stream Client', () => {
  test('should handle arbitration stream events', async () => {
    const mockRequestData = {
      policy: { /* mock policy data */ },
      opposer_evidences: [],
      defender_evidences: [],
      user_query: "test query"
    };

    const events = [];
    
    try {
      for await (const event of streamArbitrationAsync(mockRequestData)) {
        events.push(event);
        
        if (event.type === 'complete') break;
      }
    } catch (error) {
      // Handle test errors
    }

    expect(events.length).toBeGreaterThan(0);
    expect(events[events.length - 1].type).toBe('complete');
  });
});
```

## Performance Considerations

1. **Connection Pooling**: Reuse HTTP connections when possible
2. **Backpressure**: Handle cases where the client can't process events fast enough
3. **Memory Management**: Clean up event listeners and close streams properly
4. **Timeout Handling**: Set appropriate timeouts for long-running streams

## Security Considerations

1. **Authentication**: Add proper authentication headers if required
2. **Input Validation**: Validate request data before sending
3. **HTTPS**: Use HTTPS in production environments
4. **Rate Limiting**: Implement client-side rate limiting to prevent abuse

## Dependencies

```json
{
  "dependencies": {
    "eventsource": "^2.0.2",
    "node-fetch": "^3.3.2",
    "uuid": "^9.0.0"
  },
  "devDependencies": {
    "jest": "^29.0.0"
  }
}
```

## Installation and Setup

```bash
# Install dependencies
npm install eventsource node-fetch uuid

# For development
npm install --save-dev jest

# Run the example
node arbitration-client.js
```

This documentation provides comprehensive guidance for integrating with the AI Arbiter streaming API using Node.js, covering multiple implementation approaches, error handling, and best practices.
