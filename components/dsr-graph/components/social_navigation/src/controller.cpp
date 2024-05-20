//
// Created by pbustos on 24/7/20.
//

#include "controller.h"
#include <algorithm>
#include <cppitertools/zip.hpp>
#include <iomanip>

void Controller::initialize(std::shared_ptr<RoboCompCommonBehavior::ParameterList> params_)
{
    qDebug()<< "Controller - " << __FUNCTION__;
    this->time = QTime::currentTime();
    this->delay = delay*1000;	//msecs
    try
    {
        MAX_ADV_SPEED = QString::fromStdString(params_->at("MaxZSpeed").value).toFloat();
        MAX_ROT_SPEED = QString::fromStdString(params_->at("MaxRotationSpeed").value).toFloat();
        MAX_SIDE_SPEED = QString::fromStdString(params_->at("MaxXSpeed").value).toFloat();
        MAX_LAG = std::stof(params_->at("MinControllerPeriod").value);
        ROBOT_RADIUS_MM =  QString::fromStdString(params_->at("RobotRadius").value).toFloat();
        qDebug()<< __FUNCTION__ << "CONTROLLER: Params from config:"  << MAX_ADV_SPEED << MAX_ROT_SPEED << MAX_SIDE_SPEED << MAX_LAG << ROBOT_RADIUS_MM;
    }
    catch (const std::out_of_range& oor)
    {
        std::cout << "CONTROLLER. Out of Range error reading parameters: " << oor.what() << '\n';
        std::terminate();
    }
}

Controller::retUpdate Controller::update(std::vector<QPointF> points, const LaserData &laser_data, const QPointF &target, const Mat::Vector6d &robotPose, const QPointF &robotNose)
{
    qDebug() << "Controller - "<< __FUNCTION__;
    if(points.size() < 2)
        return retUpdate{false, false, false, 0, 0, 0};

    // now x is forward direction and z corresponds to y, pointing leftwards
    float advVelx = 0.f, advVelz = 0.f, rotVel = 0.f;
    //auto firstPointInPath = points.front();
    bool active = true;
    bool blocked = false;
    QPointF robot = QPointF(robotPose.x(), robotPose.y());
    // Compute euclidean distance to target
    float euc_dist_to_target = QVector2D(robot - target).length();

    auto is_increasing = [](float new_val)
            { static float ant_value = 0.f;
              bool res = false;
              if( new_val - ant_value > 0 ) res = true;
              ant_value = new_val;
              return res;
            };

    // Target achieved
    if ( (points.size() < 3) and (euc_dist_to_target < FINAL_DISTANCE_TO_TARGET or is_increasing(euc_dist_to_target)))
    {
        advVelx = 0;  advVelz= 0; rotVel = 0;
        active = false;
        std::cout << std::boolalpha << __FUNCTION__ << " Target achieved. Conditions: n points < 3 " << (points.size() < 3)
                  << " dist < 100 " << (euc_dist_to_target < FINAL_DISTANCE_TO_TARGET)
                  << " der_dist > 0 " << is_increasing(euc_dist_to_target)  << std::endl;
        return std::make_tuple(true, blocked, active, advVelz, advVelx, rotVel);  //side, adv, rot
    }

    /// Compute rotational speed
    QLineF robot_to_nose(robot, robotNose);
    float angle = rewrapAngleRestricted(qDegreesToRadians(robot_to_nose.angleTo(QLineF(robotNose, points[1]))));
    if(angle >= 0) rotVel = std::clamp(angle, 0.f, MAX_ROT_SPEED);
    else rotVel = std::clamp(angle, -MAX_ROT_SPEED, 0.f);
    if(euc_dist_to_target < 4*FINAL_DISTANCE_TO_TARGET)
        rotVel = 0.f;

    /// Compute advance speed
    std::min(advVelx = MAX_ADV_SPEED * exponentialFunction(rotVel, 1.5, 0.1, 0), euc_dist_to_target);

    /// Compute bumper-away speed
    QVector2D total{0, 0};
    const auto &[angles, dists] = laser_data;
    for (const auto &[angle, dist] : iter::zip(angles, dists))
    {
        float limit = (fabs(ROBOT_LENGTH / 2.f * sin(angle)) + fabs(ROBOT_LENGTH / 2.f * cos(angle))) + 200;
        float diff = limit - dist;
        if (diff >= 0)
            total = total + QVector2D(-diff * cos(angle), -diff * sin(angle));
    }
    QVector2D bumperVel = total * KB;  // Parameter set in slidebar
    if (abs(bumperVel.y()) < MAX_SIDE_SPEED)
        advVelz = bumperVel.y();

    return std::make_tuple (true, blocked, active, advVelz, advVelx, rotVel); //side, adv, rot
}

/////////////////////////////////////////////////////////////////////////////////////////////////
/// Auxiliary functions
/////////////////////////////////////////////////////////////////////////////////////////////////

// compute max de gauss(value) where gauss(x)=y  y min
float Controller::exponentialFunction(float value, float xValue, float yValue, float min)
{
    if (yValue <= 0)
        return 1.f;
    float landa = -fabs(xValue) / log(yValue);
    float res = exp(-fabs(value) / landa);
    return std::max(res, min);
}

float Controller::rewrapAngleRestricted(const float angle)
{
    if (angle > M_PI)
        return angle - M_PI * 2;
    else if (angle < -M_PI)
        return angle + M_PI * 2;
    else
        return angle;
}


////////////////////////////////////

//Controller::retUpdate Controller::update(std::vector<QPointF> points, const RoboCompLaser::TLaserData &laserData, const QPointF &target, const QVec &robotPose, const QPointF &robotNose)
//{
//    qDebug() << "Controller - "<< __FUNCTION__;
//    if(points.empty())
//        return retUpdate{false, false, false, 0, 0, 0};
//
//    float advVelx = 0.f, advVelz = 0.f, rotVel = 0.f;
//    auto firstPointInPath = points.front();
//    bool active = true;
//    bool blocked = false;
//    QPointF robot = QPointF(robotPose.x(), robotPose.z());
//
//    // Compute euclidean distance to target
//    float euc_dist_to_target = QVector2D(robot - target).length();
//    // qDebug()<< "DISTANCE TO TARGET " << euc_dist_to_target << "NUM POINTS "<< points.size();
//
//    if (points.size() < 3 and euc_dist_to_target < FINAL_DISTANCE_TO_TARGET)
//    {
//        qDebug()<< "·························";
//        qDebug()<< "···· TARGET ACHIEVED ····";
//        qDebug()<< "·························";
//
//        advVelz = 0;
//        rotVel = 0;
//        active = false;
//        return std::make_tuple(true, blocked, active, advVelx, advVelz,rotVel);
//    }
//
//    // Proceed through path
//    // Compute rotation speed. We use angle between robot's nose and line between first and sucessive points
//    // as an estimation of curvature ahead
//
//    std::vector<float> angles;
//    auto lim = std::min(6, (int)points.size());
//    QLineF nose(robot, robotNose);
//
//    for (auto &&i : iter::range(1, lim))
//        angles.push_back(rewrapAngleRestricted(qDegreesToRadians(nose.angleTo(QLineF(firstPointInPath, points[i])))));
//
//    auto min_angle = std::min(angles.begin(), angles.end());
//    // auto min_angle = std::min_element(angles.begin(), angles.end());
//
//    if (min_angle != angles.end())
//    {
//        rotVel = 1.2 * *min_angle;
//        if (fabs(rotVel) > MAX_ROT_SPEED)
//            rotVel = rotVel / fabs(rotVel) * MAX_ROT_SPEED;
//    }
//    else
//    {
//        rotVel = 0;
////        qDebug() << __FUNCTION__ << "rotvel = 0";
//    }
//
//    //      qDebug()<< "[CONTROLLER]"<<__FUNCTION__<< "Angles "<<angles << "min_angle " << *min_angle;
//    //      qDebug()<<"rotVel" <<rotVel;
//
//    // Compute advance speed
//    std::min(advVelz = MAX_ADV_SPEED * exponentialFunction(rotVel, 0.6, 0.2, 0), euc_dist_to_target);
//
//    // Compute bumper-away speed
//    QVector2D total{0, 0};
//    for (const auto &l : laserData)
//    {
//        float limit = (fabs(ROBOT_LENGTH / 2.f * sin(l.angle)) + fabs(ROBOT_LENGTH / 2.f * cos(l.angle))) + 200;
//        float diff = limit - l.dist;
//        if (diff >= 0)
//            total = total + QVector2D(-diff * sin(l.angle), -diff * cos(l.angle));
//    }
//    QVector2D bumperVel = total * KB;  // Parameter set in slidebar
//    if (abs(bumperVel.x()) < MAX_SIDE_SPEED)
//        advVelx = bumperVel.x();
//
//    return std::make_tuple (true, blocked, active, advVelx, advVelz,rotVel);
//}
