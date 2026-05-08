import React, { useState } from 'react';
import {
    Text,
    TextInput,
    TouchableOpacity,
    StyleSheet,
    ScrollView,
    Alert,
    Modal,
    View,
} from 'react-native';

import { BASE_URL } from '../services/api';

type Props = {
    goToLogin: () => void;
};

const bloodTypes = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', '0+', '0-'];
const genders = ['Female', 'Male', 'Other'];

export default function RegisterScreen({ goToLogin }: Props) {
    const [fullName, setFullName] = useState('');
    const [tcNo, setTcNo] = useState('');
    const [email, setEmail] = useState('');
    const [emergencyEmail1, setEmergencyEmail1] = useState('');
    const [emergencyEmail2, setEmergencyEmail2] = useState('');
    const [password, setPassword] = useState('');
    const [bloodType, setBloodType] = useState('');
    const [diseases, setDiseases] = useState('');
    const [birthDate, setBirthDate] = useState('');
    const [gender, setGender] = useState('');
    const [loading, setLoading] = useState(false);

    const [bloodModalVisible, setBloodModalVisible] = useState(false);
    const [genderModalVisible, setGenderModalVisible] = useState(false);

    const handleEmailChange = (text: string) => {
        setEmail(text.trim().toLowerCase());
    };

    const handleEmergencyEmail1Change = (text: string) => {
        setEmergencyEmail1(text.trim().toLowerCase());
    };

    const handleEmergencyEmail2Change = (text: string) => {
        setEmergencyEmail2(text.trim().toLowerCase());
    };

    const handleTcChange = (text: string) => {
        const onlyNumbers = text.replace(/[^0-9]/g, '');
        setTcNo(onlyNumbers);
    };

    const handleRegister = async () => {
        const cleanFullName = fullName.trim();
        const cleanEmail = email.trim().toLowerCase();
        const cleanPassword = password.trim();
        const cleanEmergencyEmail1 = emergencyEmail1.trim().toLowerCase();
        const cleanEmergencyEmail2 = emergencyEmail2.trim().toLowerCase();

        if (
            !cleanFullName ||
            !tcNo ||
            !cleanEmail ||
            !cleanPassword ||
            !bloodType ||
            !birthDate ||
            !gender ||
            !cleanEmergencyEmail1 ||
            !cleanEmergencyEmail2
        ) {
            Alert.alert('Missing Information', 'Please fill in all required fields.');
            return;
        }

        if (!/^[0-9]{11}$/.test(tcNo)) {
            Alert.alert(
                'Invalid TC ID',
                'TC identity number must contain only numbers and must be 11 digits.',
            );
            return;
        }

        try {
            setLoading(true);

            const response = await fetch(`${BASE_URL}/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    full_name: cleanFullName,
                    email: cleanEmail,
                    phone: tcNo,
                    password: cleanPassword,
                }),
            });

            const data = await response.json();

            if (!response.ok || !data.success) {
                Alert.alert(
                    'Register Failed',
                    data.message || 'Account could not be created.',
                );
                return;
            }

            Alert.alert('Success', 'Account created successfully!');
            goToLogin();
        } catch (error) {
            console.log('Register Error:', error);
            Alert.alert('Connection Error', 'Backend connection failed.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <ScrollView
            style={styles.scroll}
            contentContainerStyle={styles.container}
            keyboardShouldPersistTaps="handled">
            <Text style={styles.title}>Create Account</Text>

            <TextInput
                style={styles.input}
                placeholder="Full Name and Surname"
                placeholderTextColor="#aaa"
                value={fullName}
                onChangeText={setFullName}
            />

            <TextInput
                style={styles.input}
                placeholder="Email Address"
                placeholderTextColor="#aaa"
                value={email}
                onChangeText={handleEmailChange}
                keyboardType="email-address"
                autoCapitalize="none"
                autoCorrect={false}
            />

            <TextInput
                style={styles.input}
                placeholder="Emergency Contact Email 1"
                placeholderTextColor="#aaa"
                value={emergencyEmail1}
                onChangeText={handleEmergencyEmail1Change}
                keyboardType="email-address"
                autoCapitalize="none"
                autoCorrect={false}
            />

            <TextInput
                style={styles.input}
                placeholder="Emergency Contact Email 2"
                placeholderTextColor="#aaa"
                value={emergencyEmail2}
                onChangeText={handleEmergencyEmail2Change}
                keyboardType="email-address"
                autoCapitalize="none"
                autoCorrect={false}
            />

            <TextInput
                style={styles.input}
                placeholder="Password"
                placeholderTextColor="#aaa"
                value={password}
                onChangeText={setPassword}
                secureTextEntry
                autoCapitalize="none"
                autoCorrect={false}
            />

            <TextInput
                style={styles.input}
                placeholder="11-digit TC Identity Number"
                placeholderTextColor="#aaa"
                value={tcNo}
                onChangeText={handleTcChange}
                keyboardType="number-pad"
                maxLength={11}
            />

            <TouchableOpacity
                style={styles.selectBox}
                onPress={() => setBloodModalVisible(true)}>
                <Text style={bloodType ? styles.selectText : styles.placeholderText}>
                    {bloodType || 'Select Blood Type'}
                </Text>
            </TouchableOpacity>

            <TextInput
                style={[styles.input, styles.largeInput]}
                placeholder="Existing Diseases (if any)"
                placeholderTextColor="#aaa"
                value={diseases}
                onChangeText={setDiseases}
                multiline
            />

            <TextInput
                style={styles.input}
                placeholder="Birth Date (DD/MM/YYYY)"
                placeholderTextColor="#aaa"
                value={birthDate}
                onChangeText={setBirthDate}
            />

            <TouchableOpacity
                style={styles.selectBox}
                onPress={() => setGenderModalVisible(true)}>
                <Text style={gender ? styles.selectText : styles.placeholderText}>
                    {gender || 'Select Gender'}
                </Text>
            </TouchableOpacity>

            <TouchableOpacity
                style={[styles.button, loading && styles.disabledButton]}
                onPress={handleRegister}
                disabled={loading}>
                <Text style={styles.buttonText}>
                    {loading ? 'Registering...' : 'Register'}
                </Text>
            </TouchableOpacity>

            <TouchableOpacity onPress={goToLogin}>
                <Text style={styles.link}>Already have an account? Login</Text>
            </TouchableOpacity>

            <Modal transparent visible={bloodModalVisible} animationType="slide">
                <View style={styles.modalBackground}>
                    <View style={styles.modalBox}>
                        <Text style={styles.modalTitle}>Select Blood Type</Text>

                        {bloodTypes.map(item => (
                            <TouchableOpacity
                                key={item}
                                style={styles.option}
                                onPress={() => {
                                    setBloodType(item);
                                    setBloodModalVisible(false);
                                }}>
                                <Text style={styles.optionText}>{item}</Text>
                            </TouchableOpacity>
                        ))}

                        <TouchableOpacity onPress={() => setBloodModalVisible(false)}>
                            <Text style={styles.cancelText}>Cancel</Text>
                        </TouchableOpacity>
                    </View>
                </View>
            </Modal>

            <Modal transparent visible={genderModalVisible} animationType="slide">
                <View style={styles.modalBackground}>
                    <View style={styles.modalBox}>
                        <Text style={styles.modalTitle}>Select Gender</Text>

                        {genders.map(item => (
                            <TouchableOpacity
                                key={item}
                                style={styles.option}
                                onPress={() => {
                                    setGender(item);
                                    setGenderModalVisible(false);
                                }}>
                                <Text style={styles.optionText}>{item}</Text>
                            </TouchableOpacity>
                        ))}

                        <TouchableOpacity onPress={() => setGenderModalVisible(false)}>
                            <Text style={styles.cancelText}>Cancel</Text>
                        </TouchableOpacity>
                    </View>
                </View>
            </Modal>
        </ScrollView>
    );
}

const styles = StyleSheet.create({
    scroll: {
        flex: 1,
        backgroundColor: '#DCEAF7',
    },
    container: {
        padding: 25,
        paddingTop: 70,
        paddingBottom: 50,
    },
    title: {
        fontSize: 30,
        fontWeight: 'bold',
        color: '#2F7A8A',
        marginBottom: 25,
        textAlign: 'center',
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
    button: {
        backgroundColor: '#A72608',
        padding: 15,
        borderRadius: 10,
        alignItems: 'center',
        marginTop: 10,
        marginBottom: 20,
    },
    disabledButton: {
        opacity: 0.6,
    },
    buttonText: {
        color: 'white',
        fontWeight: 'bold',
        fontSize: 18,
    },
    link: {
        textAlign: 'center',
        color: '#003049',
        fontSize: 15,
        marginBottom: 20,
    },
    modalBackground: {
        flex: 1,
        backgroundColor: 'rgba(0,0,0,0.45)',
        justifyContent: 'center',
        padding: 25,
    },
    modalBox: {
        backgroundColor: '#DCEAF7',
        borderRadius: 18,
        padding: 20,
    },
    modalTitle: {
        fontSize: 22,
        fontWeight: 'bold',
        color: '#003049',
        textAlign: 'center',
        marginBottom: 15,
    },
    option: {
        backgroundColor: '#003049',
        padding: 14,
        borderRadius: 10,
        marginBottom: 10,
    },
    optionText: {
        color: 'white',
        textAlign: 'center',
        fontSize: 16,
        fontWeight: 'bold',
    },
    cancelText: {
        color: '#A72608',
        textAlign: 'center',
        fontWeight: 'bold',
        marginTop: 10,
        fontSize: 16,
    },
});