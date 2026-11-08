// Groups of "label  value" rows, two groups side by side when the card is wide enough.
import QtQuick
import QtQuick.Layouts

Flow {
    id: grid
    property var groups: []
    property string textFont: ""
    property string numberFont: ""
    property real baseSize: 11
    readonly property bool twoColumns: width >= 300
    readonly property real blockWidth: twoColumns ? (width - spacing) / 2 : width
    spacing: 16

    Repeater {
        model: grid.groups
        Column {
            width: grid.blockWidth
            spacing: 3
            Text {
                text: modelData.title
                color: theme.text_muted
                font.family: grid.textFont; font.pointSize: grid.baseSize - 1
                font.weight: Font.DemiBold; font.capitalization: Font.AllUppercase
                bottomPadding: 4
            }
            Repeater {
                model: modelData.rows
                RowLayout {
                    width: grid.blockWidth
                    spacing: 6
                    Text {
                        Layout.fillWidth: true
                        text: modelData.label
                        color: theme.text_muted
                        elide: Text.ElideRight
                        font.family: grid.textFont; font.pointSize: grid.baseSize - 0.5
                    }
                    Text {
                        text: modelData.value
                        color: modelData.color
                        font.family: grid.numberFont; font.pointSize: grid.baseSize - 0.5
                        font.weight: Font.DemiBold
                    }
                }
            }
        }
    }
}
