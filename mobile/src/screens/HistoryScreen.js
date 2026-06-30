import React, {useState, useCallback} from 'react';
import {
  View, Text, StyleSheet, FlatList, RefreshControl,
  ActivityIndicator,
} from 'react-native';
import {useFocusEffect} from '@react-navigation/native';
import {attendanceAPI} from '../services/api';

const statusColors = {
  present: '#22c55e',
  late: '#f59e0b',
  absent: '#ef4444',
};

const HistoryScreen = () => {
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const loadHistory = async () => {
    try {
      const res = await attendanceAPI.myAttendance();
      setRecords(res.data);
    } catch (e) {
      console.log(e);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useFocusEffect(
    useCallback(() => {
      loadHistory();
    }, []),
  );

  const renderItem = ({item}) => (
    <View style={styles.card}>
      <View style={styles.cardRow}>
        <View style={styles.left}>
          <Text style={styles.courseCode}>{item.course_code}</Text>
          <Text style={styles.courseName}>{item.course_name}</Text>
          <Text style={styles.date}>{item.session_date}</Text>
          <Text style={styles.time}>{item.scan_time?.slice(11, 19) || '--:--:--'}</Text>
        </View>
        <View style={styles.right}>
          <View style={[styles.badge, {backgroundColor: statusColors[item.status] || '#94a3b8'}]}>
            <Text style={styles.badgeText}>{item.status?.toUpperCase()}</Text>
          </View>
        </View>
      </View>
    </View>
  );

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color="#2563eb" />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Attendance History</Text>
      <FlatList
        data={records}
        keyExtractor={item => String(item.id)}
        renderItem={renderItem}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={() => { setRefreshing(true); loadHistory(); }} />
        }
        ListEmptyComponent={
          <Text style={styles.empty}>No attendance records found</Text>
        }
        contentContainerStyle={records.length === 0 ? {flex: 1, justifyContent: 'center'} : null}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {flex: 1, backgroundColor: '#f0f4ff', padding: 15},
  center: {flex: 1, justifyContent: 'center', alignItems: 'center'},
  title: {fontSize: 22, fontWeight: 'bold', color: '#1e3a5f', marginBottom: 15},
  card: {
    backgroundColor: '#fff', borderRadius: 12, padding: 14,
    marginBottom: 10, elevation: 1, shadowColor: '#000',
    shadowOffset: {width: 0, height: 1}, shadowOpacity: 0.05, shadowRadius: 2,
  },
  cardRow: {flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center'},
  left: {flex: 1},
  courseCode: {fontSize: 16, fontWeight: 'bold', color: '#2563eb'},
  courseName: {fontSize: 13, color: '#475569', marginTop: 2},
  date: {fontSize: 12, color: '#94a3b8', marginTop: 4},
  time: {fontSize: 12, color: '#94a3b8'},
  right: {marginLeft: 10},
  badge: {paddingHorizontal: 12, paddingVertical: 6, borderRadius: 8},
  badgeText: {color: '#fff', fontSize: 12, fontWeight: 'bold'},
  empty: {textAlign: 'center', color: '#64748b', fontSize: 16},
});

export default HistoryScreen;
