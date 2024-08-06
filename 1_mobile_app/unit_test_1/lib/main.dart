import 'package:flutter/material.dart';
import 'dart:ui';
import 'package:svg_path_parser/svg_path_parser.dart';
import 'dart:typed_data';

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: Scaffold(
        appBar: AppBar(
          title: Text('Multi-Segment SVG Path Animation'),
        ),
        body: Center(
          child: AnimatedSvgPathWidget(),
        ),
      ),
    );
  }
}

class AnimatedSvgPathWidget extends StatefulWidget {
  @override
  _AnimatedSvgPathWidgetState createState() => _AnimatedSvgPathWidgetState();
}

class _AnimatedSvgPathWidgetState extends State<AnimatedSvgPathWidget> with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Path _path;

  @override
  Path scalePath(Path originalPath, double scale) {
  // 创建一个 4x4 缩放矩阵
  final matrix = Float64List(16)
    ..[0] = scale   // X轴缩放
    ..[5] = scale   // Y轴缩放
    ..[10] = 1.0    // Z轴缩放（对2D路径没效果，但需要设置为1）
    ..[15] = 1.0;   // 矩阵的最后一个元素需要设置为1

  // 使用矩阵变换原始路径
  return originalPath.transform(matrix);
}
  void initState() {
    super.initState();
    const svgPathData = "M768 192a189.76 189.76 0 0 1 168 98.56c17.28 30.976 25.472 63.488 24.512 97.472a194.624 194.624 0 0 1-28.992 96.512 185.216 185.216 0 0 1-72.96 69.504 192 192 0 0 1-98.56 22.016c-16 57.344-46.464 103.488-91.456 138.496-44.992 35.008-97.152 52.8-156.48 53.504H320c-72.704-1.984-133.056-27.008-181.056-75.008S66.048 584.704 64 512.064v-352c0-9.344 3.008-17.024 9.024-23.04a31.168 31.168 0 0 1 23.04-8.96h640c9.344 0 16.96 3.008 22.976 8.96 6.016 6.016 8.96 13.696 8.96 23.04v32V192z m0 64v256c36.032-0.64 66.176-13.184 90.496-37.504 24.32-24.32 36.8-54.528 37.504-90.496-0.64-36.032-13.184-66.176-37.504-90.496-24.32-24.32-54.528-36.8-90.496-37.504zM96 832h640c9.344 0 17.024 3.008 23.04 8.96 5.952 6.016 8.96 13.696 8.96 23.04a31.168 31.168 0 0 1-8.96 23.04 31.168 31.168 0 0 1-23.04 8.96h-640a31.168 31.168 0 0 1-23.04-8.96 31.168 31.168 0 0 1-8.96-23.04c0-9.344 3.008-17.024 8.96-23.04A31.168 31.168 0 0 1 96 832zM128 192v320c1.344 54.656 20.032 100.032 56 136S265.28 702.656 320 704h192c54.656-1.344 100.032-20.032 136-56S702.656 566.72 704 512V192H128z";  // Example with multiple segments
    _path = parseSvgPath(svgPathData);
    double scale = 0.2;  // Apply scaling if needed
    _path = scalePath(_path, scale);  // Apply the scaling function

    _controller = AnimationController(
      vsync: this,
      duration: Duration(seconds: 3),
    )..repeat();
  }

  @override
  Widget build(BuildContext context) {
    return CustomPaint(
      painter: AnimatedSvgPathPainter(_path, _controller),
      size: Size(200, 200),
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
      ..color = Colors.blue
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2;

    for (PathMetric pathMetric in path.computeMetrics()) {
      Path extractedPath = pathMetric.extractPath(0, pathMetric.length * animation.value);
      canvas.drawPath(extractedPath, paint);
    }
  }

  @override
  bool shouldRepaint(covariant AnimatedSvgPathPainter oldDelegate) => animation != oldDelegate.animation;
}
