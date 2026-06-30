import React, {useState} from 'react';
import {
  View, Text, TextInput, StyleSheet, KeyboardAvoidingView,
  Platform, Alert, ScrollView, TouchableOpacity,
} from 'react-native';
import {authAPI} from '../services/api';
import LoadingButton from '../components/LoadingButton';

const RegisterScreen = ({navigation}) => {
  const [form, setForm] = useState({
    username: '', email: '', password: '',
    first_name: '', last_name: '', phone: '',
  });
  const [loading, setLoading] = useState(false);

  const updateField = (field, value) => setForm(prev => ({...prev, [field]: value}));

  const handleRegister = async () => {
    if (!form.username || !form.email || !form.password) {
      Alert.alert('Error', 'Username, email, and password are required');
      return;
    }
    setLoading(true);
    try {
      await authAPI.register({...form, role: 'student'});
      Alert.alert('Success', 'Registration successful. Please login.', [
        {text: 'OK', onPress: () => navigation.goBack()},
      ]);
    } catch (e) {
      const msg = e.response?.data || 'Registration failed';
      Alert.alert('Error', typeof msg === 'string' ? msg : JSON.stringify(msg));
    } finally {
      setLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}>
      <ScrollView contentContainerStyle={styles.scroll}>
        <Text style={styles.title}>Create Account</Text>
        <TextInput
          style={styles.input} placeholder="Username *"
          value={form.username} onChangeText={v => updateField('username', v)}
          autoCapitalize="none"
        />
        <TextInput
          style={styles.input} placeholder="Email *"
          value={form.email} onChangeText={v => updateField('email', v)}
          keyboardType="email-address" autoCapitalize="none"
        />
        <TextInput
          style={styles.input} placeholder="Password *"
          value={form.password} onChangeText={v => updateField('password', v)}
          secureTextEntry
        />
        <TextInput
          style={styles.input} placeholder="First Name"
          value={form.first_name} onChangeText={v => updateField('first_name', v)}
        />
        <TextInput
          style={styles.input} placeholder="Last Name"
          value={form.last_name} onChangeText={v => updateField('last_name', v)}
        />
        <TextInput
          style={styles.input} placeholder="Phone"
          value={form.phone} onChangeText={v => updateField('phone', v)}
          keyboardType="phone-pad"
        />
        <LoadingButton title="Register" onPress={handleRegister} loading={loading} />
        <TouchableOpacity onPress={() => navigation.goBack()}>
          <Text style={styles.link}>Already have an account? Login</Text>
        </TouchableOpacity>
      </ScrollView>
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  container: {flex: 1, backgroundColor: '#f0f4ff'},
  scroll: {padding: 30, paddingTop: 60},
  title: {fontSize: 24, fontWeight: 'bold', color: '#1e3a5f', marginBottom: 20, textAlign: 'center'},
  input: {
    backgroundColor: '#fff', padding: 15, borderRadius: 10,
    marginBottom: 12, borderWidth: 1, borderColor: '#e2e8f0', fontSize: 16,
  },
  link: {textAlign: 'center', color: '#2563eb', marginTop: 15, fontSize: 14},
});

export default RegisterScreen;
