// Six areas of play on a 1-20 scale; the polygon glides from one player to the next.
import QtQuick
import QtQuick.Shapes

Item {
    id: hex
    objectName: "hexagon"

    property var areas: []
    property string textFont: ""
    property string numberFont: ""
    property real baseSize: 11

    function areaValue(i) { return areas.length > i ? areas[i].value : 0 }
    property real v0: areaValue(0)
    property real v1: areaValue(1)
    property real v2: areaValue(2)
    property real v3: areaValue(3)
    property real v4: areaValue(4)
    property real v5: areaValue(5)
    Behavior on v0 { NumberAnimation { duration: theme.animationMs; easing.type: Easing.OutCubic } }
    Behavior on v1 { NumberAnimation { duration: theme.animationMs; easing.type: Easing.OutCubic } }
    Behavior on v2 { NumberAnimation { duration: theme.animationMs; easing.type: Easing.OutCubic } }
    Behavior on v3 { NumberAnimation { duration: theme.animationMs; easing.type: Easing.OutCubic } }
    Behavior on v4 { NumberAnimation { duration: theme.animationMs; easing.type: Easing.OutCubic } }
    Behavior on v5 { NumberAnimation { duration: theme.animationMs; easing.type: Easing.OutCubic } }

    readonly property real cx: width / 2
    readonly property real cy: height / 2
    readonly property real radius: Math.max(Math.min(width / 2 - 64, height / 2 - 40), 10)

    function point(i, v) {
        var angle = Math.PI / 3 * i - Math.PI / 2
        var r = radius * Math.max(v, 0) / 20
        return Qt.point(cx + r * Math.cos(angle), cy + r * Math.sin(angle))
    }
    function ring(v) {
        var points = []
        for (var i = 0; i <= 6; i++) points.push(point(i % 6, v))
        return points
    }
    function spokes() {
        var lines = []
        for (var i = 0; i < 6; i++) lines.push([point(i, 0), point(i, 20)])
        return lines
    }

    Shape {
        anchors.fill: parent
        preferredRendererType: Shape.CurveRenderer
        ShapePath {
            strokeColor: theme.border; strokeWidth: 1; fillColor: "transparent"
            PathPolyline { path: hex.ring(20 / 3) }
        }
        ShapePath {
            strokeColor: theme.border; strokeWidth: 1; fillColor: "transparent"
            PathPolyline { path: hex.ring(40 / 3) }
        }
        ShapePath {
            strokeColor: theme.border; strokeWidth: 1; fillColor: "transparent"
            PathPolyline { path: hex.ring(20) }
        }
        ShapePath {
            strokeColor: theme.border; strokeWidth: 1; fillColor: "transparent"
            PathMultiline { paths: hex.spokes() }
        }
    }

    readonly property var shape: [point(0, v0), point(1, v1), point(2, v2), point(3, v3),
                                  point(4, v4), point(5, v5), point(0, v0)]
    Shape {  // the fill, kept translucent on its own so the outline stays crisp
        anchors.fill: parent
        opacity: 0.22
        preferredRendererType: Shape.CurveRenderer
        ShapePath {
            strokeColor: "transparent"; fillColor: theme.accent
            PathPolyline { path: hex.shape }
        }
    }
    Shape {
        anchors.fill: parent
        preferredRendererType: Shape.CurveRenderer
        ShapePath {
            strokeColor: theme.accent; strokeWidth: 2; fillColor: "transparent"
            joinStyle: ShapePath.RoundJoin
            PathPolyline { path: hex.shape }
        }
    }
    Repeater {
        model: 6
        Rectangle {
            readonly property point at: hex.point(index, [hex.v0, hex.v1, hex.v2, hex.v3, hex.v4, hex.v5][index])
            x: at.x - 3; y: at.y - 3; width: 6; height: 6; radius: 3
            color: theme.accent
        }
    }

    Repeater {
        model: 6
        Column {
            readonly property point at: hex.point(index, 26.5)
            x: at.x - width / 2
            y: at.y - height / 2
            spacing: 0
            Text {
                anchors.horizontalCenter: parent.horizontalCenter
                text: hex.areas.length > index ? hex.areas[index].name : ""
                color: theme.text_muted
                font.family: hex.textFont; font.pointSize: hex.baseSize - 1
            }
            Text {
                anchors.horizontalCenter: parent.horizontalCenter
                text: hex.areas.length > index ? hex.areas[index].label : ""
                color: theme.text
                font.family: hex.numberFont; font.pointSize: hex.baseSize; font.weight: Font.DemiBold
            }
        }
    }
}
