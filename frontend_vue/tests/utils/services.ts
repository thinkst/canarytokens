import axios from 'axios';

export const createTestingJob = async () => {
  try {
    const form = {
      action: 'create-job',
    }
    const response = await axios.post('https://fktzgnofp3ulkr7ri6shfvhoei0avrrs.lambda-url.eu-west-1.on.aws/', form);
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
    const response = await axios.post('https://fktzgnofp3ulkr7ri6shfvhoei0avrrs.lambda-url.eu-west-1.on.aws/', form);
    return response.data;
  } catch (error) {
    console.error('Error registering token data:', error);
    throw error;
  }
};
