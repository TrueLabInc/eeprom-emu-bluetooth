#ifndef MAIN_H_
#define MAIN_H_

#include <iostream>
using std::cout;
using std::endl;

class PinChange;

namespace pins{
	enum pins{
		pin_a = 1,
		pin_b = 2,
		pin_c = 3,
		pin_d = 4,
	};
}

class Bclass{
public:
	static PinChange p1;
};

class PinChange{
private:
	pins::pins p;
public:
	PinChange(pins::pins p) : p(p) {};
	void operator=(bool s){
		if(s)
			cout << p << "=" << "hi" << endl;
		else
			cout << p << "=" << "low" << endl;
	}
};

PinChange Bclass::p1 = PinChange(pins::pin_b);

#endif /* MAIN_H_ */
