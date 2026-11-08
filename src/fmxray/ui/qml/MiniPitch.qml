// The 15 positions on a small pitch (attack at the top), each with the player's rating.
import QtQuick

Rectangle {
    id: pitch
    property var positions: []
    property string textFont: ""
    property string numberFont: ""
    property real baseSize: 11
    readonly property real cellWidth: width / 3
    readonly property real cellHeight: 44

    height: cellHeight * 7 + 8
    radius: 8
    color: theme.raised
    border.color: theme.border

    Rectangle {  // halfway line
        x: 8; width: parent.width - 16; height: 1
        y: pitch.cellHeight * 3.5
        color: theme.border
    }

    Repeater {
        model: pitch.positions
        Rectangle {
            x: modelData.column * pitch.cellWidth + 6
            y: modelData.row * pitch.cellHeight + 6
            width: pitch.cellWidth - 12
            height: pitch.cellHeight - 8
            radius: 6
            color: modelData.value === "" ? "transparent" : theme.surface
            border.color: modelData.value === "" ? "transparent" : theme.border
            Row {
                anchors.centerIn: parent
                spacing: 6
                Text {
                    text: modelData.label
                    color: theme.text_muted
                    font.family: pitch.textFont; font.pointSize: pitch.baseSize - 1
                }
                Text {
                    text: modelData.value
                    color: modelData.color
                    font.family: pitch.numberFont; font.pointSize: pitch.baseSize
                    font.weight: Font.DemiBold
                }
            }
        }
    }
}
