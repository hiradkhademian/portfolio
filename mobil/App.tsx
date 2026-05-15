import React, { useEffect, useState } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';

import LoginScreen from './src/screens/LoginScreen';
import RegisterScreen from './src/screens/RegisterScreen';
import HomeScreen from './src/screens/HomeScreen';

export type User = {
    id?: number;
    full_name: string;
    email: string;
    phone: string;
    password?: string;
    tcNo?: string;
    bloodType?: string;
    diseases?: string;
    birthDate?: string;
    gender?: string;
    emergencyEmail1?: string;
    emergencyEmail2?: string;
};

type Screen = 'login' | 'register' | 'home';

const TOKEN_KEY = 'authToken';
const USER_KEY = 'loggedUser';

export default function App(): React.JSX.Element {
    const [screen, setScreen] = useState<Screen>('login');
    const [user, setUser] = useState<User | null>(null);

    useEffect(() => {
        checkLogin();
    }, []);

    const checkLogin = async () => {
        try {
            const token = await AsyncStorage.getItem(TOKEN_KEY);
            const storedUser = await AsyncStorage.getItem(USER_KEY);

            if (token && storedUser) {
                setUser(JSON.parse(storedUser));
                setScreen('home');
            }
        } catch (error) {
            console.log(error);
        }
    };

    const handleLoginSuccess = async (
        token: string,
        loggedUser: User,
    ) => {
        await AsyncStorage.setItem(TOKEN_KEY, token);

        await AsyncStorage.setItem(
            USER_KEY,
            JSON.stringify(loggedUser),
        );

        setUser(loggedUser);
        setScreen('home');
    };

    const handleLogout = async () => {
        await AsyncStorage.removeItem(TOKEN_KEY);
        await AsyncStorage.removeItem(USER_KEY);

        setUser(null);
        setScreen('login');
    };

    if (screen === 'login') {
        return (
            <LoginScreen
                goToRegister={() => setScreen('register')}
                onLoginSuccess={handleLoginSuccess}
            />
        );
    }

    if (screen === 'register') {
        return (
            <RegisterScreen
                goToLogin={() => setScreen('login')}
            />
        );
    }

    return (
        <HomeScreen
            user={user}
            onLogout={handleLogout}
        />
    );
}