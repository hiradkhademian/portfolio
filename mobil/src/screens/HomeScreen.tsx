import React, {useEffect, useRef, useState} from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Modal,
  TextInput,
  ScrollView,
  Alert,
} from 'react-native';

import AsyncStorage from '@react-native-async-storage/async-storage';
import Geolocation from '@react-native-community/geolocation';
import {BASE_URL} from '../services/api';
import type {User} from '../../App';

type Props = {
  user: User | null;
  onUpdateUser: (updatedUser: User) => void;
  onLogout: () => void;
};

const bloodTypes = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', '0+', '0-'];
const genders = ['Female', 'Male', 'Other'];

export default function HomeScreen({user, onUpdateUser, onLogout}: Props) {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [emergencyEmail1, setEmergencyEmail1] = useState('');
  const [emergencyEmail2, setEmergencyEmail2] = useState('');
  const [tcNo, setTcNo] = useState('');
  const [bloodType, setBloodType] = useState('');
  const [diseases, setDiseases] = useState('');
  const [birthDate, setBirthDate] = useState('');
  const [gender, setGender] = useState('');

  const [isCountingDown, setIsCountingDown] = useState(false);
  const [countdown, setCountdown] = useState(7);
  const [isSharing, setIsSharing] = useState(false);
  const [sharingSeconds, setSharingSeconds] = useState(0);
  const [locationLink, setLocationLink] = useState('');
  const [emergencyTriggered, setEmergencyTriggered] = useState(false);
  const [currentEmergencyId, setCurrentEmergencyId] = useState<number | null>(null);
  const emergencyTriggeredRef = useRef(false);
  const currentEmergencyIdRef = useRef<number | null>(null);

  const countdownIntervalRef =
    useRef<ReturnType<typeof setInterval> | null>(null);
  const sharingTimerRef =
    useRef<ReturnType<typeof setInterval> | null>(null);
  const locationWatchIdRef = useRef<number | null>(null);

  useEffect(() => {
    Geolocation.requestAuthorization();

    return () => {
      clearAllTimers();
      stopLocationWatch();
    };
  }, []);

  const openSidebar = () => {
    if (user) {
      setFullName(user.fullName || '');
      setEmail(user.email || '');
      setEmergencyEmail1(user.emergencyEmail1 || '');
      setEmergencyEmail2(user.emergencyEmail2 || '');
      setTcNo(user.tcNo || '');
      setBloodType(user.bloodType || '');
      setDiseases(user.diseases || '');
      setBirthDate(user.birthDate || '');
      setGender(user.gender || '');
    }

    setIsSidebarOpen(true);
  };

  const clearAllTimers = () => {
    if (countdownIntervalRef.current) {
      clearInterval(countdownIntervalRef.current);
      countdownIntervalRef.current = null;
    }

    if (sharingTimerRef.current) {
      clearInterval(sharingTimerRef.current);
      sharingTimerRef.current = null;
    }
  };

  const stopLocationWatch = () => {
    if (locationWatchIdRef.current !== null) {
      Geolocation.clearWatch(locationWatchIdRef.current);
      locationWatchIdRef.current = null;
    }
  };

  const handleTcChange = (text: string) => {
    setTcNo(text.replace(/[^0-9]/g, ''));
  };

  const openBloodTypePicker = () => {
    Alert.alert('Select Blood Type', '', [
      ...bloodTypes.map(item => ({
        text: item,
        onPress: () => setBloodType(item),
      })),
      {text: 'Cancel', style: 'cancel' as const},
    ]);
  };

  const openGenderPicker = () => {
    Alert.alert('Select Gender', '', [
      ...genders.map(item => ({
        text: item,
        onPress: () => setGender(item),
      })),
      {text: 'Cancel', style: 'cancel' as const},
    ]);
  };

  const handleSOS = () => {
    if (isCountingDown || isSharing) {
      return;
    }

    setIsCountingDown(true);
    setCountdown(7);

    countdownIntervalRef.current = setInterval(() => {
      setCountdown(prev => {
        if (prev <= 1) {
          clearAllTimers();
          setIsCountingDown(false);
          startLocationSharing();
          return 0;
        }

        return prev - 1;
      });
    }, 1000);
  };

  const startLocationSharing = () => {
    setIsSharing(true);
    setSharingSeconds(0);

    sharingTimerRef.current = setInterval(() => {
      setSharingSeconds(prev => prev + 1);
    }, 1000);

    locationWatchIdRef.current = Geolocation.watchPosition(
      async position => {
        const {latitude, longitude} = position.coords;
        const googleMapsLink =
          `https://www.google.com/maps?q=${latitude},${longitude}`;

        setLocationLink(googleMapsLink);

        if (!emergencyTriggeredRef.current) {
          emergencyTriggeredRef.current = true;
          setEmergencyTriggered(true);
          try {
            const token = await AsyncStorage.getItem('authToken');
            const response = await fetch(`${BASE_URL}/emergency/trigger`, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`,
              },
              body: JSON.stringify({
                latitude,
                longitude,
              }),
            });

            const data = await response.json();
            if (data.success) {
              setCurrentEmergencyId(data.emergency.id);
              currentEmergencyIdRef.current = data.emergency.id;
              Alert.alert('Emergency Alert Sent', 'Help is on the way!');
            } else {
              Alert.alert('Error', data.message || 'Failed to send emergency alert');
            }
          } catch (error) {
            console.log('Emergency trigger error:', error);
            Alert.alert('Error', 'Failed to send emergency alert');
          }
        } else if (currentEmergencyIdRef.current) {
          try {
            const token = await AsyncStorage.getItem('authToken');
            await fetch(`${BASE_URL}/emergency/${currentEmergencyIdRef.current}/location`, {
              method: 'PUT',
              headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`,
              },
              body: JSON.stringify({
                latitude,
                longitude,
              }),
            });
          } catch (error) {
            console.log('Location update error:', error);
          }
        }
      },
      error => {
        console.log('Location Error:', error);
      },
      {
        enableHighAccuracy: true,
        distanceFilter: 1,
        interval: 3000,
        fastestInterval: 2000,
      },
    );
  };

  const stopSharing = () => {
    clearAllTimers();
    stopLocationWatch();

    setIsCountingDown(false);
    setCountdown(7);
    setIsSharing(false);
    setSharingSeconds(0);
    setLocationLink('');
    setEmergencyTriggered(false);
    setCurrentEmergencyId(null);
    emergencyTriggeredRef.current = false;
    currentEmergencyIdRef.current = null;
  };

  const saveProfile = () => {
    if (!user) {
      return;
    }

    if (!/^[0-9]{11}$/.test(tcNo)) {
      Alert.alert(
        'Invalid TC ID',
        'TC identity number must contain only numbers and must be 11 digits.',
      );
      return;
    }

    const updatedUser: User = {
      ...user,
      fullName: fullName.trim(),
      email: email.trim().toLowerCase(),
      password: user.password,
      tcNo,
      bloodType,
      diseases: diseases.trim(),
      birthDate: birthDate.trim(),
      gender,
      emergencyEmail1: emergencyEmail1.trim().toLowerCase(),
      emergencyEmail2: emergencyEmail2.trim().toLowerCase(),
    };

    onUpdateUser(updatedUser);
    setIsSidebarOpen(false);
  };

  const handleLogoutPress = () => {
    stopSharing();
    setIsSidebarOpen(false);
    onLogout();
  };

  const formatTime = (seconds: number) => {
    const min = Math.floor(seconds / 60);
    const sec = seconds % 60;

    return `${min.toString().padStart(2, '0')}:${sec
      .toString()
      .padStart(2, '0')}`;
  };

  return (
    <View style={styles.container}>
      <TouchableOpacity style={styles.menuButton} onPress={openSidebar}>
        <Text style={styles.menuText}>☰</Text>
      </TouchableOpacity>

      <TouchableOpacity style={styles.logoutButton} onPress={handleLogoutPress}>
        <Text style={styles.logoutText}>Çıkış</Text>
      </TouchableOpacity>

      <Text style={styles.title}>Emergency App</Text>

      <TouchableOpacity
        style={[
          styles.sosButton,
          isCountingDown && styles.countdownButton,
          isSharing && styles.sharingButton,
        ]}
        onPress={handleSOS}
        disabled={isCountingDown || isSharing}>
        <Text style={styles.sosText}>
          {isCountingDown
            ? countdown
            : isSharing
            ? formatTime(sharingSeconds)
            : 'SOS'}
        </Text>
      </TouchableOpacity>

      {(isCountingDown || isSharing) && (
        <>
          {isSharing && (
            <>
              <Text style={styles.activeText}>Konum paylaşımı aktif.</Text>
              <Text style={styles.locationText}>
                {locationLink || 'Konum alınıyor...'}
              </Text>
            </>
          )}

          <TouchableOpacity style={styles.stopButton} onPress={stopSharing}>
            <Text style={styles.stopButtonText}>Durdur</Text>
          </TouchableOpacity>
        </>
      )}

      <Modal visible={isSidebarOpen} transparent animationType="slide">
        <View style={styles.modalOverlay}>
          <View style={styles.sidebar}>
            <ScrollView keyboardShouldPersistTaps="handled">
              <Text style={styles.sidebarTitle}>User Profile</Text>

              <Text style={styles.label}>Full Name and Surname</Text>
              <TextInput
                style={styles.input}
                value={fullName}
                onChangeText={setFullName}
                placeholder="Full Name and Surname"
                placeholderTextColor="#aaa"
              />

              <Text style={styles.label}>Email Address</Text>
              <TextInput
                style={styles.input}
                value={email}
                onChangeText={text => setEmail(text.toLowerCase())}
                placeholder="Email Address"
                placeholderTextColor="#aaa"
                keyboardType="email-address"
                autoCapitalize="none"
                autoCorrect={false}
              />

              <Text style={styles.label}>Emergency Contact Email 1</Text>
              <TextInput
                style={styles.input}
                value={emergencyEmail1}
                onChangeText={text =>
                  setEmergencyEmail1(text.trim().toLowerCase())
                }
                placeholder="Emergency Contact Email 1"
                placeholderTextColor="#aaa"
                keyboardType="email-address"
                autoCapitalize="none"
                autoCorrect={false}
              />

              <Text style={styles.label}>Emergency Contact Email 2</Text>
              <TextInput
                style={styles.input}
                value={emergencyEmail2}
                onChangeText={text =>
                  setEmergencyEmail2(text.trim().toLowerCase())
                }
                placeholder="Emergency Contact Email 2"
                placeholderTextColor="#aaa"
                keyboardType="email-address"
                autoCapitalize="none"
                autoCorrect={false}
              />

              <Text style={styles.label}>TC Identity Number</Text>
              <TextInput
                style={styles.input}
                value={tcNo}
                onChangeText={handleTcChange}
                placeholder="11-digit TC Identity Number"
                placeholderTextColor="#aaa"
                keyboardType="number-pad"
                maxLength={11}
              />

              <Text style={styles.label}>Blood Type</Text>
              <TouchableOpacity
                style={styles.selectBox}
                onPress={openBloodTypePicker}>
                <Text
                  style={bloodType ? styles.selectText : styles.placeholderText}>
                  {bloodType || 'Select Blood Type'}
                </Text>
              </TouchableOpacity>

              <Text style={styles.label}>Existing Diseases</Text>
              <TextInput
                style={[styles.input, styles.largeInput]}
                value={diseases}
                onChangeText={setDiseases}
                placeholder="Existing Diseases (if any)"
                placeholderTextColor="#aaa"
                multiline
              />

              <Text style={styles.label}>Birth Date</Text>
              <TextInput
                style={styles.input}
                value={birthDate}
                onChangeText={setBirthDate}
                placeholder="Birth Date (DD/MM/YYYY)"
                placeholderTextColor="#aaa"
              />

              <Text style={styles.label}>Gender</Text>
              <TouchableOpacity
                style={styles.selectBox}
                onPress={openGenderPicker}>
                <Text style={gender ? styles.selectText : styles.placeholderText}>
                  {gender || 'Select Gender'}
                </Text>
              </TouchableOpacity>

              <TouchableOpacity style={styles.saveButton} onPress={saveProfile}>
                <Text style={styles.saveButtonText}>Save Changes</Text>
              </TouchableOpacity>

              <TouchableOpacity
                style={styles.closeButton}
                onPress={() => setIsSidebarOpen(false)}>
                <Text style={styles.closeButtonText}>Close</Text>
              </TouchableOpacity>
            </ScrollView>
          </View>
        </View>
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#DCEAF7',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 20,
  },
  menuButton: {
    position: 'absolute',
    top: 55,
    left: 25,
    zIndex: 10,
  },
  menuText: {
    fontSize: 34,
    color: '#003049',
    fontWeight: 'bold',
  },
  logoutButton: {
    position: 'absolute',
    top: 58,
    right: 25,
    backgroundColor: '#A72608',
    paddingVertical: 8,
    paddingHorizontal: 16,
    borderRadius: 10,
    zIndex: 10,
  },
  logoutText: {
    color: 'white',
    fontWeight: 'bold',
    fontSize: 14,
  },
  title: {
    fontSize: 28,
    marginBottom: 40,
    color: '#2F7A8A',
    fontWeight: 'bold',
  },
  sosButton: {
    width: 220,
    height: 220,
    borderRadius: 110,
    backgroundColor: '#A72608',
    alignItems: 'center',
    justifyContent: 'center',
  },
  countdownButton: {
    backgroundColor: '#D97706',
  },
  sharingButton: {
    backgroundColor: '#0B6E4F',
  },
  sosText: {
    color: 'white',
    fontSize: 55,
    fontWeight: 'bold',
  },
  activeText: {
    marginTop: 30,
    fontSize: 20,
    fontWeight: 'bold',
    color: '#0B6E4F',
    textAlign: 'center',
  },
  locationText: {
    marginTop: 12,
    fontSize: 14,
    color: '#003049',
    textAlign: 'center',
    paddingHorizontal: 20,
  },
  stopButton: {
    marginTop: 25,
    backgroundColor: '#001219',
    paddingVertical: 14,
    paddingHorizontal: 45,
    borderRadius: 12,
  },
  stopButtonText: {
    color: 'white',
    fontWeight: 'bold',
    fontSize: 18,
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.35)',
    alignItems: 'flex-start',
  },
  sidebar: {
    width: '82%',
    height: '100%',
    backgroundColor: '#DCEAF7',
    padding: 25,
    paddingTop: 70,
  },
  sidebarTitle: {
    fontSize: 30,
    fontWeight: 'bold',
    color: '#2F7A8A',
    marginBottom: 25,
    textAlign: 'center',
  },
  label: {
    color: '#003049',
    fontSize: 15,
    fontWeight: 'bold',
    marginBottom: 6,
    marginLeft: 3,
  },
  input: {
    backgroundColor: '#003049',
    borderRadius: 10,
    padding: 15,
    marginBottom: 15,
    color: 'white',
    fontSize: 16,
  },
  largeInput: {
    height: 90,
    textAlignVertical: 'top',
  },
  selectBox: {
    backgroundColor: '#003049',
    borderRadius: 10,
    padding: 15,
    marginBottom: 15,
  },
  selectText: {
    color: 'white',
    fontSize: 16,
  },
  placeholderText: {
    color: '#aaa',
    fontSize: 16,
  },
  saveButton: {
    backgroundColor: '#A72608',
    padding: 15,
    borderRadius: 10,
    alignItems: 'center',
    marginTop: 10,
    marginBottom: 15,
  },
  saveButtonText: {
    color: 'white',
    fontWeight: 'bold',
    fontSize: 18,
  },
  closeButton: {
    backgroundColor: '#001219',
    padding: 15,
    borderRadius: 10,
    alignItems: 'center',
    marginBottom: 40,
  },
  closeButtonText: {
    color: 'white',
    fontWeight: 'bold',
    fontSize: 18,
  },
});