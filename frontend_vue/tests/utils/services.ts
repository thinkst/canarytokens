import axios from 'axios';

const TESTING_SERVICE_URL = process.env.TESTING_SERVICE_URL || '';

export const createTestingJob = async () => {
  try {
    const form = {
      action: 'create-job',
    }
    const response = await axios.post(TESTING_SERVICE_URL, form);
    return response.data;
  } catch (error) {
    console.error('Error creating testing job:', error);
    throw error;
  }
};

export const registerTokenData = async (jobId: string, items: any[]) => {
  const form = {
    action: 'add-urls',
    job_id: jobId,
    items,
  };
  try {
    const response = await axios.post(TESTING_SERVICE_URL, form);
    return response.data;
  } catch (error) {
    console.error('Error registering token data:', error);
    throw error;
  }
};
