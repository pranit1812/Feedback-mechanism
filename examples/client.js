/**
 * Example client-side JavaScript code to send feedback to the dashboard API
 * 
 * This is just a reference implementation that can be integrated into any front-end website.
 */

// Function to send feedback to the dashboard
async function sendFeedback(feedbackData) {
  try {
    // Replace with your actual deployed Vercel app URL
    const apiUrl = 'https://your-vercel-app-url.vercel.app/api/feedback';
    
    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(feedbackData),
    });
    
    const result = await response.json();
    
    if (!response.ok) {
      throw new Error(result.error || 'Failed to send feedback');
    }
    
    return result;
  } catch (error) {
    console.error('Error sending feedback:', error);
    throw error;
  }
}

// Example usage - Positive feedback
const positiveFeedback = {
  id: `feedback-${Date.now()}`,
  projectName: 'My Project',
  query: 'How do I implement authentication?',
  answer: 'You can use JWT tokens for authentication...',
  sentiment: 'up',
  'user.id': 'user-123',
  'user.email': 'user@example.com',
  searchMethod: 'direct'
};

// Example usage - Negative feedback
const negativeFeedback = {
  id: `feedback-${Date.now() + 1}`,
  projectName: 'My Project',
  query: 'How do I deploy to production?',
  answer: 'You need to configure your deployment settings...',
  sentiment: 'down',
  'user.id': 'user-456',
  'user.email': 'another-user@example.com',
  searchMethod: 'search'
};

// Example usage - Comment feedback
const commentFeedback = {
  id: `feedback-${Date.now() + 2}`,
  projectName: 'My Project',
  query: 'What is the best database for my app?',
  answer: 'It depends on your specific requirements...',
  sentiment: 'comment',
  'user.id': 'user-789',
  'user.email': 'third-user@example.com',
  searchMethod: 'recommended',
  commentText: 'This was helpful, but I would like more specific examples.'
};

// Usage example (commented out for reference)
/*
sendFeedback(positiveFeedback)
  .then(result => console.log('Feedback sent successfully:', result))
  .catch(error => console.error('Failed to send feedback:', error));
*/ 