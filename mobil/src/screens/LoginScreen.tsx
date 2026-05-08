import React, { useState } from 'react';
import {
    View,
    Text,
    TextInput,
    TouchableOpacity,
    StyleSheet,
    Alert,
    Image,
} from 'react-native';

import { BASE_URL } from '../services/api';

type User = {
    id?: number;
    full_name: string;
    email: string;
    phone: string;
};

type Props = {
    goToRegister: () => void;
    onLoginSuccess: (
        token: string,
        user: User,
    ) => void;
};

export default function LoginScreen({
    goToRegister,
    onLoginSuccess,
}: Props) {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);

    const handleLoginPress = async () => {
        if (!email || !password) {
            Alert.alert(
                'Missing Information',
                'Please enter email and password.',
            );
            return;
        }

        try {
            setLoading(true);

            const response = await fetch(
                `${BASE_URL}/login`,
                {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        email: email.trim().toLowerCase(),
                        password: password.trim(),
                    }),
                },
            );

            const data = await response.json();

            if (!response.ok || !data.success) {
                Alert.alert(
                    'Login Failed',
                    data.message || 'Invalid email or password.',
                );
                return;
            }

            onLoginSuccess(data.token, data.user);
        } catch (error) {
            console.log(error);

            Alert.alert(
                'Connection Error',
                'Backend connection failed.',
            );
        } finally {
            setLoading(false);
        }
    };

    return (
        <View style={styles.container}>
            <Image
                source={require('../../assets/logo.png')}
                style={styles.logo}
                resizeMode="contain"
            />

            <Text style={styles.title}>
                Emergency Response App
            </Text>

            <TextInput
                style={styles.input}
                placeholder="Email"
                placeholderTextColor="#aaa"
                value={email}
                onChangeText={text =>
                    setEmail(text.toLowerCase())
                }
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

            <TouchableOpacity
                style={styles.button}
                onPress={handleLoginPress}
                disabled={loading}>

                <Text style={styles.buttonText}>
                    {loading ? 'Loading...' : 'Login'}
                </Text>
            </TouchableOpacity>

            <TouchableOpacity onPress={goToRegister}>
                <Text style={styles.link}>
                    Don't have an account? Register
                </Text>
            </TouchableOpacity>
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#DCEAF7',
        justifyContent: 'center',
        padding: 25,
    },

    logo: {
        width: 150,
        height: 150,
        alignSelf: 'center',
        marginBottom: 20,
    },

    title: {
        fontSize: 30,
        fontWeight: 'bold',
        color: '#2F7A8A',
        marginBottom: 35,
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

    button: {
        backgroundColor: '#E5989B',
        padding: 15,
        borderRadius: 10,
        alignItems: 'center',
        marginBottom: 20,
    },

    buttonText: {
        color: 'white',
        fontWeight: 'bold',
        fontSize: 16,
    },

    link: {
        textAlign: 'center',
        color: '#003049',
    },
});