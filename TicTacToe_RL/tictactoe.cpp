#include "tictactoe.h"
#include <QMessageBox>
#include <fstream>
#include <iostream>
#include <string>
#include <float.h>
TicTacToe::TicTacToe(QWidget *parent) : QMainWindow(parent), playerTurn(true), moveCount(0) {
    centralWidget = new QWidget(this);
    gridLayout = new QGridLayout(centralWidget);

    for (int i = 0; i < 9; ++i) {
        QPushButton *button = new QPushButton("");
        button->setSizePolicy(QSizePolicy::Preferred, QSizePolicy::Preferred);
        button->setFont(QFont("Arial", 24));
        buttons.push_back(button);
        gridLayout->addWidget(button, i / 3, i % 3);
        connect(button, &QPushButton::clicked, this, &TicTacToe::handleButtonClick);
    }

    setCentralWidget(centralWidget);
    setWindowTitle("Tic Tac Toe");
    resize(300, 300);

    std::ifstream f("D:\\CS\\Machine Learning\\TicTacToe_RL\\TicTacToe_RL\\Qtable_0.json");
    if (!f)
        std::cout << "-1";
    try {
        f >> data;
    } catch (const json::parse_error& e) {
        std::cerr << "Failed to parse the JSON file: " << e.what() << std::endl;
        return ;
    }

}

TicTacToe::~TicTacToe() {
    for (QPushButton *button : buttons) {
        delete button;
    }
    delete gridLayout;
    delete centralWidget;
}

void TicTacToe::handleButtonClick() {
    QPushButton *clickedButton = qobject_cast<QPushButton*>(sender());

    if (!clickedButton || !clickedButton->text().isEmpty()) {
        return;
    }


    clickedButton->setText("X");

    ++moveCount;

    if(checkWin())
        return;

    int i = getNextMove();

    ++moveCount;
    if (i == -1) {
        clickedButton->setText("Err");
        return;
    }
    if(checkWin())
        return;
    buttons[i]->setText("O");
    checkWin();


}

int TicTacToe::getNextMove() {
    char state[10] = {' ',' ',' ',' ',' ',' ',' ',' ',' ','\0'};
    char hash[11] = {' ',' ',' ',' ',' ',' ',' ',' ',' ',' ','\0'};
    int possible_moves[9] = {0};
    double highest_Q = -DBL_MAX;
    int best_move = -1; // Should implement a way to randomly choose between possible moves if there is no highest_Q > 0;
    for(int i = 0; i < buttons.size(); i++) {
        if (buttons[i]->text().isEmpty()) {
            possible_moves[i] = 1;
            continue;
        }
        state[i] = buttons[i]->text().toLocal8Bit().data()[0];
    }
    for(int i = 0; i < 10;i++) {
        hash[i] = state[i];
    }
    for (int i = 0; i < 9; i++) {
        if(possible_moves[i] == 0)
            continue;
        hash[9] = (char)((int)'0' + i);
        auto a = (double)data[hash];
        if(highest_Q < a) {
            highest_Q = a;
            best_move = i;
        }
    }


    std::cout << hash << " "<< best_move << " "<< highest_Q<< std::endl;
    return best_move;
}

bool TicTacToe::checkWin() {
    const int winConditions[8][3] = {
        {0, 1, 2}, {3, 4, 5}, {6, 7, 8}, // rows
        {0, 3, 6}, {1, 4, 7}, {2, 5, 8}, // columns
        {0, 4, 8}, {2, 4, 6}             // diagonals
    };

    for (auto &condition : winConditions) {
        if (buttons[condition[0]]->text() == buttons[condition[1]]->text() &&
            buttons[condition[1]]->text() == buttons[condition[2]]->text() &&
            !buttons[condition[0]]->text().isEmpty()) {
            QString winner = buttons[condition[0]]->text();
            QMessageBox::information(this, "Tic Tac Toe", winner + " wins!");
            resetGame();
            return true;
        }
    }

    if (moveCount == 9) {
        QMessageBox::information(this, "Tic Tac Toe", "It's a draw!");
        resetGame();
        return true;
    }
    return false;
}

void TicTacToe::resetGame() {
    for (QPushButton *button : buttons) {
        button->setText("");
    }
    playerTurn = true;
    moveCount = 0;

}
