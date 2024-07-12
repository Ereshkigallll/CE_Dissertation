import 'package:flutter/material.dart';
import 'package:intl/intl.dart';  // Used for formatting the time
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_database/firebase_database.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp();
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Flutter Demo',
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ),
      home: MyHomePage(),
    );
  }
}

class MyHomePage extends StatefulWidget {
  @override
  _MyHomePageState createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  final TextEditingController _controller = TextEditingController();
  String _currentSelectedValue = 'Coke';
  final List<String> _dropdownValues = [
    'Coke', 'Coffee', 'Sprite', 'Water', 'Fanta', 'Orange Juice'
  ];

  void _sendDataToFirebase() async {
    final databaseReference = FirebaseDatabase.instance.reference().child('sensorData');
    try {
      await databaseReference.push().set({
        'device': 'Mobile Phone',
        'level': int.parse(_controller.text),
        'timestamp': DateFormat('yyyy-MM-dd HH:mm:ss').format(DateTime.now()),
        'type': _currentSelectedValue,
      });
      // Clear the text field
      _controller.clear();
      // Show confirmation dialog
      _showConfirmationDialog('Success', 'Data sent successfully!');
    } catch (e) {
      // If an error occurs, show an error message
      _showConfirmationDialog('Error', 'Failed to send data: $e');
    }
  }

  void _showConfirmationDialog(String title, String content) {
    showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: Text(title),
          content: Text(content),
          actions: <Widget>[
            TextButton(
              child: const Text('OK'),
              onPressed: () {
                Navigator.of(context).pop(); // Close the dialog
              },
            ),
          ],
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Send Data to Firebase'),
      ),
      body: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: <Widget>[
          TextField(
            controller: _controller,
            decoration: InputDecoration(
              labelText: 'Enter level',
            ),
            keyboardType: TextInputType.number,
          ),
          DropdownButton<String>(
            value: _currentSelectedValue,
            onChanged: (String? newValue) {
              if (newValue != null) {
                setState(() {
                  _currentSelectedValue = newValue;
                });
              }
            },
            items: _dropdownValues.map<DropdownMenuItem<String>>((String value) {
              return DropdownMenuItem<String>(
                value: value,
                child: Text(value),
              );
            }).toList(),
          ),
          ElevatedButton(
            onPressed: _sendDataToFirebase,
            child: const Text('Send'),
          ),
        ],
      ),
    );
  }
}
