import 'package:flutter/material.dart';
import 'package:intl/intl.dart'; // Used for formatting the time
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_database/firebase_database.dart';
import 'dart:ui';
import 'package:svg_path_parser/svg_path_parser.dart';
import 'dart:typed_data';
import 'package:material_text_fields/material_text_fields.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:cool_dropdown/models/cool_dropdown_item.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp();
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'HydroTrack',
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ),
      home: AnimatedSvgPathWidget(),
    );
  }
}

class AnimatedSvgPathWidget extends StatefulWidget {
  @override
  _AnimatedSvgPathWidgetState createState() => _AnimatedSvgPathWidgetState();
}

class _AnimatedSvgPathWidgetState extends State<AnimatedSvgPathWidget>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Path _path;

  Path scalePath(Path originalPath, double scale) {
    final matrix = Float64List(16)
      ..[0] = scale // X axis scaling
      ..[5] = scale // Y axis scaling
      ..[10] = 1.0 // Z axis scaling (no effect in 2D but needs to be set)
      ..[15] = 1.0; // last element of the matrix needs to be 1

    return originalPath.transform(matrix);
  }

  @override
  void initState() {
    super.initState();
    const svgPathData =
        "M768 192a189.76 189.76 0 0 1 168 98.56c17.28 30.976 25.472 63.488 24.512 97.472a194.624 194.624 0 0 1-28.992 96.512 185.216 185.216 0 0 1-72.96 69.504 192 192 0 0 1-98.56 22.016c-16 57.344-46.464 103.488-91.456 138.496-44.992 35.008-97.152 52.8-156.48 53.504H320c-72.704-1.984-133.056-27.008-181.056-75.008S66.048 584.704 64 512.064v-352c0-9.344 3.008-17.024 9.024-23.04a31.168 31.168 0 0 1 23.04-8.96h640c9.344 0 16.96 3.008 22.976 8.96 6.016 6.016 8.96 13.696 8.96 23.04v32V192z m0 64v256c36.032-0.64 66.176-13.184 90.496-37.504 24.32-24.32 36.8-54.528 37.504-90.496-0.64-36.032-13.184-66.176-37.504-90.496-24.32-24.32-54.528-36.8-90.496-37.504zM96 832h640c9.344 0 17.024 3.008 23.04 8.96 5.952 6.016 8.96 13.696 8.96 23.04a31.168 31.168 0 0 1-8.96 23.04 31.168 31.168 0 0 1-23.04 8.96h-640a31.168 31.168 0 0 1-23.04-8.96 31.168 31.168 0 0 1-8.96-23.04c0-9.344 3.008-17.024 8.96-23.04A31.168 31.168 0 0 1 96 832zM128 192v320c1.344 54.656 20.032 100.032 56 136S265.28 702.656 320 704h192c54.656-1.344 100.032-20.032 136-56S702.656 566.72 704 512V192H128z";
    _path = parseSvgPath(svgPathData);
    double scale = 0.2; // Apply scaling if needed
    _path = scalePath(_path, scale);

    _controller = AnimationController(
      vsync: this,
      duration: Duration(seconds: 2),
    );

    _controller.forward().then((_) {
      Navigator.pushReplacement(
          context, MaterialPageRoute(builder: (context) => MyHomePage()));
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Color(0xfff1f4f1),
      body: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min, // 使用min使列内容大小由子项决定
          children: <Widget>[
            CustomPaint(
              painter: AnimatedSvgPathPainter(_path, _controller),
              size: Size(200, 200),
            ),
            SizedBox(height: 20), // 添加一些间隔
            Text(
              'HydroTrack',
              style: TextStyle(
                fontFamily: 'Chillax',
                fontSize: 36,
                fontWeight: FontWeight.w700,
                color: Color(0xff477cb3),
              ),
            ),
            Text(
              'Your Daily Water Intake Recorder',
              style: TextStyle(
                fontFamily: 'Chillax',
                fontSize: 18,
                fontWeight: FontWeight.w400,
                color: Color(0xffa7ceed),
              ),
            ),
          ],
        ),
      ),
    );
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }
}

class AnimatedSvgPathPainter extends CustomPainter {
  final Path path;
  final Animation<double> animation;

  AnimatedSvgPathPainter(this.path, this.animation) : super(repaint: animation);

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Color(0xFFa7ceed)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 5;

    for (PathMetric pathMetric in path.computeMetrics()) {
      Path extractedPath =
          pathMetric.extractPath(0, pathMetric.length * animation.value);
      canvas.drawPath(extractedPath, paint);
    }
  }

  @override
  bool shouldRepaint(covariant AnimatedSvgPathPainter oldDelegate) =>
      animation != oldDelegate.animation;
}

// Your existing MyHomePage class
class MyHomePage extends StatefulWidget {
  @override
  _MyHomePageState createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  final TextEditingController _controller = TextEditingController();
  String _currentSelectedValue = 'Water';
  final List<String> _dropdownValues = [
    'Coke',
    'Coffee',
    'Water',
    'Fanta',
    'Juice'
  ];

  void _sendDataToFirebase() async {
    final databaseReference =
        FirebaseDatabase.instance.reference().child('sensorData');
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
              child: Text('OK'),
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
      backgroundColor: Color(0xfff1f4f1),
      appBar: AppBar(
        backgroundColor: Color(0xfff1f4f1),
        title: Text('HydroTrack',
            style: TextStyle(
                fontFamily: 'Chillax',
                color: Color(0xff477cb3),
                fontSize: 24,
                fontWeight: FontWeight.w600)),
        centerTitle: true,
      ),
      body: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: <Widget>[
          Padding(
            padding:
                const EdgeInsets.symmetric(horizontal: 50.0), // 根据需求调整水平内边距
            child: MaterialTextField(
              keyboardType: TextInputType.number,
              hint: 'Enter level', // 用 hint 替代 labelText
              textInputAction: TextInputAction.next,
              prefixIcon: SvgPicture.asset(
                'assets/logos/water.svg',
                colorFilter:
                    const ColorFilter.mode(Color(0xFF4F989E), BlendMode.srcIn),
                height: 35.0,
                width: 35.0,
              ), // 前缀图标，确保图标文件存在
              controller: _controller,
              validator: (String? value) {
                if (value!.isEmpty) {
                  return 'Please enter a value';
                }
                return null;
              },
            ),
          ),
          SizedBox(height: 20),
          DropdownButton<String>(
            value: _currentSelectedValue,
            onChanged: (String? newValue) {
              if (newValue != null) {
                setState(() {
                  _currentSelectedValue = newValue;
                });
              }
            },
            items:
                _dropdownValues.map<DropdownMenuItem<String>>((String value) {
              return DropdownMenuItem<String>(
                value: value,
                child: Text(value),
              );
            }).toList(),
          ),
          SizedBox(height: 20),
          ElevatedButton(
            onPressed: _sendDataToFirebase,
            child: Text('Send',
                style: TextStyle(
                    color: Color(0xfff1f4f1),
                    fontSize: 20,
                    fontFamily: 'Chillax',
                    fontWeight: FontWeight.w500)),
            style: ButtonStyle(
              backgroundColor: MaterialStateProperty.all(
                Color(0xffa7ceed),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
