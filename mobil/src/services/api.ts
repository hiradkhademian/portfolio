import { Platform } from 'react-native';

const LOCAL_BACKEND = 'http://127.0.0.1:5001';
const REAL_DEVICE_BACKEND = 'http://192.168.43.235:5001'; // Mac LAN IP for real device testing
const USE_REAL_DEVICE = true; // set to true when testing on your actual iPhone (Eda's iPhone)

const apiHost = process.env.API_BASE_URL
  || (USE_REAL_DEVICE ? REAL_DEVICE_BACKEND : LOCAL_BACKEND);

export const BASE_URL = `${apiHost}/api`;

// When testing on a real iPhone, set USE_REAL_DEVICE to true and update REAL_DEVICE_BACKEND
// with your Mac's LAN IP. When using the iOS simulator, leave USE_REAL_DEVICE false.
