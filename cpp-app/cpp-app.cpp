﻿#include "cpp-app.h"

int main() {
	if (std::filesystem::exists(Variables::PATH + "cache") == false) {
		std::filesystem::create_directory(Variables::PATH + "cache");
	}

	UI::Initialize();

	std::cout << "Close the window to continue!" << std::endl;

	//cv::Mat Frame = OpenCV::EmptyImage(500, 200, 3, 0, 0, 0);
	//OpenCV::ShowImage("Close the window to continue!", Frame, false);
	//OpenCV::SetWindowCaptionColor(L"Close the window to continue!", 0, 0, 0);
	//OpenCV::SetWindowBorderColor(L"Close the window to continue!", 200, 0, 0);
	//OpenCV::ShowImage("Close the window to continue!", Frame, true);

	//PyTorch::LoadExampleModel();

	//PyTorch::ExampleTensor();
	//PyTorch::Initialize("OleFranz", "PyTorch-Calculator", true);
	//PyTorch::Loaded("PyTorch-Calculator");

    SimpleWindow::Initialize(Variables::NAME, std::make_tuple(700, 400), std::make_tuple(100, 100), std::make_tuple(Variables::TAB_BAR_COLOR[0], Variables::TAB_BAR_COLOR[1], Variables::TAB_BAR_COLOR[2]), true, false, false, Variables::PATH + "app/assets/" + Variables::THEME == "Dark" ? "icon_dark.ico" : "icon_light.ico");

    auto Window = sf::RenderWindow(sf::VideoMode({700, 400}), "SFML Window");
    Window.setFramerateLimit(60);

    while (Window.isOpen()) {
        while (const std::optional Event = Window.pollEvent()) {
            if (Event->is<sf::Event::Closed>()) {
                Window.close();
            }
        }

        // Custom OpenCV UI
		UI::Example();

        Window.clear();
        Window.display();
    }

	if (Variables::BUILD_TYPE == "Release") {
		system("pause");
	}
}