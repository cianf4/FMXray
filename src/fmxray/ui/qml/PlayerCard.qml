// The player card. `card` (CardModel) gives the content, `theme` the design tokens.
import QtQuick
import QtQuick.Layouts

Rectangle {
    id: root
    color: theme.surface

    readonly property string textFont: theme.font_text
    readonly property string numberFont: theme.font_numbers
    readonly property real baseSize: parseFloat(theme.font_size)
    readonly property int ms: theme.animationMs
    property int tab: 0

    // A raised block with a soft shadow made of stacked translucent shapes: no shader
    // effect, so it renders the same on every GPU, in software and in headless tests.
    component Raised: Rectangle {
        radius: parseInt(theme.panel_radius)
        color: theme.raised
        border.color: theme.border
        Repeater {
            model: [{ grow: 1, drop: 2, alpha: 0.30 }, { grow: 3, drop: 5, alpha: 0.14 },
                    { grow: 6, drop: 8, alpha: 0.06 }]
            Rectangle {
                z: -1
                x: -modelData.grow; y: modelData.drop - modelData.grow
                width: parent.width + 2 * modelData.grow
                height: parent.height + 2 * modelData.grow
                radius: parent.radius + modelData.grow
                color: theme.shadow
                opacity: modelData.alpha
            }
        }
    }

    Text {
        anchors.centerIn: parent
        visible: card.empty
        text: qsTr("Select a player")
        color: theme.text_muted
        font.family: root.textFont; font.pointSize: root.baseSize + 1
    }

    Flickable {
        anchors.fill: parent
        anchors.margins: 12
        visible: !card.empty
        contentHeight: content.implicitHeight
        clip: true
        boundsBehavior: Flickable.StopAtBounds

        ColumnLayout {
            id: content
            width: parent.width
            spacing: 14

            // Who: initials, name, copy, "age · club · positions"
            RowLayout {
                Layout.fillWidth: true
                spacing: 12
                Rectangle {
                    implicitWidth: 46; implicitHeight: 46; radius: 23
                    color: theme.chip_background
                    border.color: theme.accent
                    Text {
                        anchors.centerIn: parent
                        text: card.initials
                        color: theme.chip_text
                        font.family: root.textFont; font.pointSize: root.baseSize + 3
                        font.weight: Font.DemiBold
                    }
                }
                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 2
                    Text {
                        Layout.fillWidth: true
                        text: card.name
                        color: theme.text
                        elide: Text.ElideRight
                        font.family: root.textFont; font.pointSize: root.baseSize + 4
                        font.weight: Font.DemiBold
                    }
                    Text {
                        Layout.fillWidth: true
                        text: card.summary
                        color: theme.text_muted
                        elide: Text.ElideRight
                        font.family: root.textFont; font.pointSize: root.baseSize
                    }
                }
                Rectangle {
                    implicitWidth: copyLabel.implicitWidth + 20
                    implicitHeight: copyLabel.implicitHeight + 10
                    radius: parseInt(theme.radius)
                    color: copyArea.containsMouse ? theme.border : theme.raised
                    border.color: theme.border
                    Behavior on color { ColorAnimation { duration: 120 } }
                    Text {
                        id: copyLabel
                        anchors.centerIn: parent
                        text: qsTr("Copy")
                        color: theme.text
                        font.family: root.textFont; font.pointSize: root.baseSize - 1
                    }
                    MouseArea {
                        id: copyArea
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: card.copyName()
                    }
                }
            }

            // Ability: CA and PA count up, the bar shows the room to grow
            Raised {
                id: abilityBox
                Layout.fillWidth: true
                implicitHeight: ability.implicitHeight + 24

                property real caShown: card.caFraction * 200
                property real paShown: card.paFraction * 200
                Behavior on caShown { NumberAnimation { duration: root.ms; easing.type: Easing.OutCubic } }
                Behavior on paShown { NumberAnimation { duration: root.ms; easing.type: Easing.OutCubic } }

                ColumnLayout {
                    id: ability
                    anchors.left: parent.left; anchors.right: parent.right
                    anchors.top: parent.top; anchors.margins: 12
                    spacing: 8
                    RowLayout {
                        spacing: 28
                        Repeater {
                            model: [
                                { caption: "CA", text: card.ca, shown: abilityBox.caShown, colour: theme.text },
                                { caption: "PA", text: card.pa, shown: abilityBox.paShown, colour: theme.accent },
                            ]
                            Column {
                                Text {
                                    text: modelData.caption
                                    color: theme.text_muted
                                    font.family: root.textFont; font.pointSize: root.baseSize - 1
                                }
                                Text {
                                    text: modelData.text === "-" ? "-" : Math.round(modelData.shown)
                                    color: modelData.colour
                                    font.family: root.numberFont; font.pointSize: root.baseSize + 15
                                    font.weight: Font.DemiBold
                                }
                            }
                        }
                    }
                    Item {
                        Layout.fillWidth: true
                        implicitHeight: 8
                        Rectangle { anchors.fill: parent; radius: 4; color: theme.border }
                        Rectangle {
                            height: parent.height; radius: 4
                            width: parent.width * card.paFraction
                            color: theme.accent; opacity: 0.35
                            Behavior on width { NumberAnimation { duration: root.ms; easing.type: Easing.OutCubic } }
                        }
                        Rectangle {
                            height: parent.height; radius: 4
                            width: parent.width * card.caFraction
                            color: theme.accent
                            Behavior on width { NumberAnimation { duration: root.ms; easing.type: Easing.OutCubic } }
                        }
                    }
                    Text {
                        text: card.growth
                        visible: text !== ""
                        color: theme.text_muted
                        font.family: root.textFont; font.pointSize: root.baseSize - 1
                    }
                }
            }

            // Areas of play
            Raised {
                Layout.fillWidth: true
                implicitHeight: 250
                Hexagon {
                    anchors.fill: parent
                    anchors.margins: 6
                    areas: card.areas
                    textFont: root.textFont
                    numberFont: root.numberFont
                    baseSize: root.baseSize
                }
            }

            // Tabs
            RowLayout {
                Layout.fillWidth: true
                spacing: 0
                Repeater {
                    model: card.tabs
                    Column {
                        Layout.fillWidth: true
                        Layout.preferredWidth: 1  // equal shares of the row
                        spacing: 4
                        Text {
                            width: parent.width
                            horizontalAlignment: Text.AlignHCenter
                            elide: Text.ElideRight
                            text: modelData.title
                            color: root.tab === index ? theme.text : theme.text_muted
                            font.family: root.textFont; font.pointSize: root.baseSize
                            font.weight: root.tab === index ? Font.DemiBold : Font.Normal
                            MouseArea {
                                anchors.fill: parent
                                cursorShape: Qt.PointingHandCursor
                                onClicked: root.tab = index
                            }
                        }
                        Rectangle {
                            width: parent.width; height: 2; radius: 1
                            color: theme.accent
                            opacity: root.tab === index ? 1 : 0
                            Behavior on opacity { NumberAnimation { duration: root.ms } }
                        }
                    }
                }
            }

            FieldGrid {
                Layout.fillWidth: true
                groups: card.tabs.length > root.tab ? card.tabs[root.tab].groups : []
                textFont: root.textFont
                numberFont: root.numberFont
                baseSize: root.baseSize
            }

            MiniPitch {
                Layout.fillWidth: true
                visible: card.tabs.length > root.tab && card.tabs[root.tab].title === qsTr("Positions")
                positions: card.positions
                textFont: root.textFont
                numberFont: root.numberFont
                baseSize: root.baseSize
            }

            Text {
                visible: card.unconfirmed
                text: qsTr("values not yet confirmed ⓘ")
                color: theme.unconfirmed
                font.family: root.textFont; font.pointSize: root.baseSize - 1
            }
        }
    }
}
