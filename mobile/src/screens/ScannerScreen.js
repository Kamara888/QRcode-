import React, {useState, useEffect} from 'react';
import {
  View, Text, StyleSheet, Alert, Vibration, ActivityIndicator,
} from 'react-native';
import {attendanceAPI} from '../services/api';
import {getUser} from '../utils/storage';

const ScannerScreen = () => {
  const [scanning, setScanning] = useState(false);
  const [result, setResult] = useState(null);
  const [status, setStatus] = useState('idle');

  const handleScan = async sessionData => {
    if (scanning) return;
    setScanning(true);
    setStatus('verifying');
    Vibration.vibrate(100);
    try {
      const user = await getUser();
      const res = await attendanceAPI.scan({
        session_id: sessionData.session_id,
        token: sessionData.token || sessionData.scan_token,
        device_info: `${Platform.OS} ${Platform.Version}`,
      });
      setResult(res.data);
      setStatus(res.data.status === 'present' ? 'success' : 'warning');
      if (res.data.message === 'Already recorded') {
        setStatus('info');
      }
    } catch (e) {
      const msg = e.response?.data?.error || 'Scan failed';
      Alert.alert('Error', msg);
      setStatus('error');
    } finally {
      setScanning(false);
    }
  };

  return (
    <View style={styles.container}>
      {status === 'idle' && (
        <View style={styles.placeholder}>
          <Text style={styles.icon}>📷</Text>
          <Text style={styles.title}>QR Scanner</Text>
          <Text style={styles.subtitle}>
            This screen uses react-native-camera to scan QR codes.{'\n\n'}
            When a QR code is detected, the attendance{'\n'}
            will be recorded automatically.
          </Text>
          <View style={styles.mockQr}>
            <Text style={styles.mockText}>QR Code Preview Area</Text>
            <Text style={styles.mockSubtext}>
              Camera feed appears here on device
            </Text>
          </View>
          <Text style={styles.note}>
            Install on a physical device to test scanning.{'\n'}
            The API endpoint POST /sessions/scan/ accepts{' '}
            {'{session_id, token}'} with Bearer JWT auth.
          </Text>
        </View>
      )}
      {status === 'verifying' && (
        <View style={styles.statusContainer}>
          <ActivityIndicator size="large" color="#2563eb" />
          <Text style={styles.statusText}>Verifying attendance...</Text>
        </View>
      )}
      {status === 'success' && result && (
        <View style={styles.successCard}>
          <Text style={styles.resultIcon}>✅</Text>
          <Text style={styles.resultTitle}>Attendance Recorded</Text>
          <Text style={styles.resultStatus}>Status: Present</Text>
          <Text style={styles.resultTime}>{result.scan_time}</Text>
        </View>
      )}
      {status === 'warning' && result && (
        <View style={[styles.successCard, {borderColor: '#f59e0b'}]}>
          <Text style={styles.resultIcon}>⚠️</Text>
          <Text style={styles.resultTitle}>Marked Late</Text>
          <Text style={styles.resultStatus}>You arrived after the grace period</Text>
          <Text style={styles.resultTime}>{result.scan_time}</Text>
        </View>
      )}
      {status === 'info' && result && (
        <View style={[styles.successCard, {borderColor: '#3b82f6'}]}>
          <Text style={styles.resultIcon}>ℹ️</Text>
          <Text style={styles.resultTitle}>Already Recorded</Text>
          <Text style={styles.resultStatus}>Status: {result.status}</Text>
          <Text style={styles.resultTime}>Scanned at: {result.scan_time}</Text>
        </View>
      )}
      {status === 'error' && (
        <View style={[styles.successCard, {borderColor: '#ef4444'}]}>
          <Text style={styles.resultIcon}>❌</Text>
          <Text style={styles.resultTitle}>Scan Failed</Text>
          <Text style={styles.resultStatus}>Please try again or contact your lecturer</Text>
        </View>
      )}
      {(status === 'success' || status === 'warning' || status === 'info' || status === 'error') && (
        <View style={styles.resetContainer}>
          <Text style={styles.timerText}>Ready to scan again in 3 seconds...</Text>
          {setTimeout(() => {
            setStatus('idle');
            setResult(null);
          }, 3000)}
        </View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {flex: 1, backgroundColor: '#f0f4ff', justifyContent: 'center', alignItems: 'center', padding: 20},
  placeholder: {alignItems: 'center'},
  icon: {fontSize: 64, marginBottom: 10},
  title: {fontSize: 24, fontWeight: 'bold', color: '#1e3a5f'},
  subtitle: {fontSize: 14, color: '#64748b', textAlign: 'center', marginTop: 10, lineHeight: 22},
  mockQr: {
    width: 250, height: 250, backgroundColor: '#1e293b', borderRadius: 16,
    justifyContent: 'center', alignItems: 'center', marginTop: 20,
    borderWidth: 3, borderColor: '#2563eb', borderStyle: 'dashed',
  },
  mockText: {color: '#94a3b8', fontSize: 16, fontWeight: '600'},
  mockSubtext: {color: '#64748b', fontSize: 12, marginTop: 5},
  note: {textAlign: 'center', color: '#94a3b8', fontSize: 12, marginTop: 20, lineHeight: 18},
  statusContainer: {alignItems: 'center'},
  statusText: {marginTop: 15, fontSize: 16, color: '#64748b'},
  successCard: {
    backgroundColor: '#fff', borderRadius: 16, padding: 30,
    alignItems: 'center', borderWidth: 2, borderColor: '#22c55e', width: '100%',
    elevation: 5, shadowColor: '#000', shadowOffset: {width: 0, height: 2},
    shadowOpacity: 0.15, shadowRadius: 6,
  },
  resultIcon: {fontSize: 48, marginBottom: 10},
  resultTitle: {fontSize: 20, fontWeight: 'bold', color: '#1e3a5f', marginBottom: 8},
  resultStatus: {fontSize: 16, color: '#475569', marginBottom: 4},
  resultTime: {fontSize: 14, color: '#94a3b8'},
  resetContainer: {marginTop: 20},
  timerText: {color: '#94a3b8', fontSize: 14},
});

export default ScannerScreen;
