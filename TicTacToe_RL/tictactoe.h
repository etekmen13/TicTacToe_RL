#ifndef TICTACTOE_H
#define TICTACTOE_H

#include <QMainWindow>
#include <QPushButton>
#include <QGridLayout>
#include <QVector>
#include "json.hpp"
using json = nlohmann::json;
class TicTacToe : public QMainWindow {
    Q_OBJECT

public:
    TicTacToe(QWidget *parent = nullptr);
    ~TicTacToe();

private slots:
    void handleButtonClick();

private:
    bool checkWin();
    void resetGame();
    int getNextMove();

    QWidget *centralWidget;
    QGridLayout *gridLayout;
    QVector<QPushButton*> buttons;
    json data;
    bool playerTurn;  // true for 'X', false for 'O'
    int moveCount;
};

#endif // TICTACTOE_H
